from crewai import Crew, Task
import logging
from crewai import Agent
#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
import os

os.environ["OPENAI_API_KEY"] = ""

llm = ChatOpenAI(model="gpt-4.1-mini")

logging.basicConfig(filename='operation.log',
                    filemode='a',
                    level=logging.INFO)
def load_sheets(folder="C:\\Users\\Jan\\Documents\\WI\\Character Sheets Txt"):
    sheets = {}
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            with open(os.path.join(folder, filename), 'r', encoding="utf8") as file:
                name = filename.replace(".txt", "")
                sheets[name] = file.read()
    return sheets


def create_character_agent(name, sheet):
    return Agent(
        role=name,
        goal=f"As {name}, ensure that all references, relationships, and secrets in my sheet are reflected in others'. Raise any inconsistencies or missing links. Provide me with the logs from the cross-check. List all the agents that were created and log their thought process.",
        backstory=sheet,
        allow_delegation=True,
        verbose=True,
        llm=llm
    )
    
    

sheets = load_sheets()
agents = [create_character_agent(name, sheet) for name, sheet in sheets.items()]

tasks = []

for agent in agents:
    task = Task(
        description=(
            "Check all character sheets for missing mirrored information (relationships, secrets, events). "
            f"This check is being done from the perspective of {agent.role}. "
            "Log any inconsistencies you find. Perform the cross check for all the sheets provided separately. "
            "Don't focus only on the first sheet provided. It is absolutely crucial and a failure to do so will be perceived as a failure. "
            "Provide the thought process for every specific character sheet. Log all the inconsistencies separately for every sheet checked. "
            "You are not allowed to stop before the task is done, nor to ask if you should continue. "
            "At the end of the task you are supposed to provide me with the summary of all the inconsistencies per-character, "
            "even if there are duplicates. Do not only focus on The Apparition—check all 11 Fae court members!"
        ),
        expected_output="A list of mismatches or missing data references between characters from your point of view.",
        agent=agent,
        # async_execution=True
    )
    tasks.append(task)

crew = Crew(
    agents=agents,
    tasks=tasks,
    verbose=True
)

result = crew.kickoff()
logging.info(result)
print(result)