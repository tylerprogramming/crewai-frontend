from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import List

load_dotenv()

# gemini-2.0-flash, used in the video, shut down on 2026-06-01:
# https://ai.google.dev/gemini-api/docs/deprecations
# Set GEMINI_MODEL in .env to try another Gemini model.
google_flash_llm = LLM(
	model=f"gemini/{os.getenv('GEMINI_MODEL', 'gemini-3.8-flash')}",
	api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
)

class ResearchOutput(BaseModel):
    summary: str
    key_points: List[str]
    quick_summary: str
    extended_summary: str
    actionable_insights: List[str]
    source_document_list: List[str]
    potential_biases_and_limitations: str

@CrewBase
class FileCrew():

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			llm=google_flash_llm
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			output_pydantic=ResearchOutput
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the FileCrew crew"""

		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)
