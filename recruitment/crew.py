from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from .tools import LinkedInTool, DatabaseTool


@CrewBase
class PharmacyTechnicianCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), LinkedInTool()],
            allow_delegation=False,
            verbose=True
        )

    @agent
    def analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['analyzer'],
            tools=[DatabaseTool()],
            allow_delegation=False,
            verbose=True
        )

    @agent
    def communicator(self) -> Agent:
        return Agent(
            config=self.agents_config['communicator'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), DatabaseTool()],
            allow_delegation=False,
            verbose=True
        )

    @agent
    def reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['reporter'],
            tools=[DatabaseTool()],
            allow_delegation=False,
            verbose=True
        )

    @task
    def search_linkedin_task(self, criteria=None) -> Task:
        return Task(
            config=self.tasks_config['search_linkedin_task'],
            agent=self.researcher(),
            input_data={"criteria": criteria if criteria else "Pharmacy Technician, United States"}
        )

    @task
    def analyze_candidates_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_candidates_task'],
            agent=self.analyzer(),
            context=[self.search_linkedin_task()]
        )

    @task
    def develop_outreach_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['develop_outreach_strategy_task'],
            agent=self.communicator(),
            context=[self.analyze_candidates_task()]
        )

    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],
            agent=self.reporter(),
            context=[self.search_linkedin_task(), self.analyze_candidates_task(), self.develop_outreach_strategy_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Pharmacy Technician recruitment crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )