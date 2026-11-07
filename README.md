# PDF Processing with Docling and CrewAI

This is a FastAPI application that uses Docling to parse PDF files and extract their content, then analyzes this content using CrewAI to generate structured reports and insights.

## 5 Steps:
1. Create Frontend with Bolt.new
2. Create FastAPI Project
3. Create Crew
4. Ngrok Static Domain
5. Connect Frontend with FastAPI

## Features

- **Document Parsing**: Uses Docling to extract text content from PDF files
- **AI Analysis**: Processes extracted content with CrewAI to generate structured reports
- **API Interface**: Simple REST API for file upload and processing
- **Markdown Export**: Returns parsed content in markdown format
- **Clean Implementation**: Proper error handling and temporary file management

> **Updated for CrewAI 1.15 (2026-11).** The video used CrewAI 0.105 and `gemini-2.0-flash`. Google shut that model down on 2026-06-01 ([Gemini deprecations](https://ai.google.dev/gemini-api/docs/deprecations)), so the crew now defaults to `gemini-3.8-flash`. `requirements.txt` lists only the packages the app imports, not the original 417-line freeze. The code may differ slightly from the video.

## Requirements

- Python 3.10 to 3.13 (CrewAI 1.15 needs >=3.10,<3.14)
- FastAPI
- Docling
- CrewAI 1.15 with the `google-genai` extra
- A Google AI Studio API key (`GOOGLE_API_KEY`)
- Other dependencies as specified in requirements.txt

## Setup

1. Clone the repository:

```bash
git clone https://github.com/tylerprogramming/crewai-frontend.git
cd crewai-frontend
```

2. Set up a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Environment variables (required):

The crew calls Gemini, so create a `.env` file in the repository root with your Google AI Studio key:

```
GOOGLE_API_KEY=your_google_api_key
# Optional: any Gemini model id, without the gemini/ prefix
GEMINI_MODEL=gemini-3.8-flash
```

`GEMINI_API_KEY` also works in place of `GOOGLE_API_KEY`. No OpenAI key is needed.

5. Run the application:

```bash
python app.py
```

The API will be available at `http://<your-local-ip>:5010`.

## API Endpoints

### Process PDF File

**Endpoint**: `/file-handler`  
**Method**: POST  
**Content-Type**: multipart/form-data

**Parameters**:
- `file`: The PDF file to parse and analyze

**Example using curl**:
```bash
curl -X POST "http://localhost:5010/file-handler" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.pdf"
```

**Example using JavaScript/Fetch**:
```javascript
const formData = new FormData();
formData.append('file', pdfFile); // pdfFile is a File object

fetch('http://localhost:5010/file-handler', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

**Response**:
```json
{
  "filename": "example.pdf",
  "markdown": "# Document Title\n\nContent in markdown format...",
  "result": {
    "summary": "One-paragraph summary...",
    "key_points": ["Point 1", "Point 2", "..."],
    "quick_summary": "Summary of the document...",
    "extended_summary": "Detailed analysis...",
    "actionable_insights": ["Insight 1", "Insight 2", "..."],
    "source_document_list": ["Document title and description..."],
    "potential_biases_and_limitations": "Discussion of biases..."
  }
}
```

## Implementation Details

### How It Works

1. **PDF Processing**:
   - The application receives a PDF file through the `/file-handler` endpoint
   - Docling's DocumentConverter processes the PDF and extracts structured content
   - The content is converted to markdown format for further processing

2. **AI Analysis**:
   - The markdown content is passed to the CrewAI system
   - A researcher agent analyzes the content according to the task definition
   - The agent generates a structured report with key points, summaries, and insights

3. **Result Delivery**:
   - Both the original markdown and the AI-generated analysis are returned to the client
   - The response includes detailed sections as specified in the task configuration

### CrewAI Task Configuration

The CrewAI system is configured to analyze documents with a specific focus. The task configuration is defined in `file_crew/src/file_crew/config/tasks.yaml` and includes:

- Extracting key points from the document
- Creating executive summaries
- Providing detailed analysis
- Suggesting actionable insights
- Identifying potential biases in the source material

## Testing

`test_pdf_parser.py` was removed from the repository (commit b903596), so test the API with the curl example above. `app.py` binds to your machine's LAN IP, not `localhost`, so use the address it prints on startup (`Starting server at http://<ip>:5010`).

## Project Structure

```
.
├── app.py                  # FastAPI application
├── requirements.txt        # Project dependencies
├── file_crew/
│   └── src/
│       └── file_crew/
│           ├── crew.py     # Agent, task and Gemini LLM
│           ├── main.py     # CrewAI integration
│           └── config/
│               └── tasks.yaml  # Task definitions for the AI analysis
```

## Troubleshooting

- **PDF Parsing Issues**: Make sure the uploaded PDF is not corrupted and doesn't have DRM protection
- **CrewAI Errors**: Check that any required environment variables are set correctly
- **API Connection Issues**: Verify that the API is running and accessible from your client


## Acknowledgements

- [Docling](https://github.com/docling-project/docling) for PDF parsing
- [CrewAI](https://github.com/joaomdmoura/crewAI) for AI agent orchestration
