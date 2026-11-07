from fastapi import FastAPI, HTTPException, Body, File, Form, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import socket
import json
from typing import List, Dict, Any
import uvicorn
import tempfile
import os
from docling.document_converter import DocumentConverter
from file_crew.src.file_crew.main import run

def get_local_ip() -> str:
    """
    Get the local IP address of the machine.
    
    Returns:
        str: The local IP address, or '127.0.0.1' if it can't be determined.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

app = FastAPI(
    title="CrewAI API",
    description="API for processing documents with Docling and CrewAI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/file-handler", response_model=Dict[str, Any])
async def file_handler_endpoint(
    file: UploadFile = File(...)
):
    """
    Process a PDF file using Docling and CrewAI.
    
    Args:
        file (UploadFile): The PDF file to process
        
    Returns:
        Dict[str, Any]: The processed results including markdown content and CrewAI analysis
        
    Raises:
        HTTPException: If there's an error processing the file
    """
    temp_file_path = None
    
    try:
        print(f"Received file: {file.filename} (type: {file.content_type}, size: {file.size})")
        
        # Validate file type
        if not file.content_type.startswith('application/pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.content_type}. Please upload a PDF file."
            )
        
        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the file
        try:
            # Initialize the DocumentConverter
            converter = DocumentConverter()
            
            # Convert the PDF document
            docling_result = converter.convert(temp_file_path)
            
            # Get the parsed content in markdown format
            markdown_content = docling_result.document.export_to_markdown()
            
            # Process with CrewAI. crewai 1.x refuses a sync kickoff() inside
            # a running event loop, so run the crew in a worker thread.
            crew_result = await run_in_threadpool(run, markdown_content)
            
            # Return the results
            return {
                "filename": file.filename,
                "markdown": markdown_content,
                "result": crew_result.model_dump()
            }
        
        finally:
            # Always clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")
    except Exception as e:
        print(f"Error in file_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint that returns basic API information."""
    return {
        "message": "Welcome to the CrewAI Document Processing API",
        "endpoints": {
            "/file-handler": "POST endpoint for processing PDF files"
        }
    }

if __name__ == "__main__":
    host_ip = get_local_ip()
    print(f"Starting server at http://{host_ip}:5010")
    uvicorn.run("app:app", host=host_ip, port=5010, reload=True)
