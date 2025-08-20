#Agent
from agno.agent import Agent
#APIs
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
#Memoria
from agno.memory.agent import AgentMemory
from agno.memory.db.sqlite import SqliteMemoryDb
#Armazenamento
from agno.storage.sqlite import SqliteStorage
#Interface
from agno.playground import Playground
#Carregar API
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())
#IMPORTAR ARQUIVO
from transcription_reader import get_creator_transcriptions, list_available_creators

copywriter = Agent(
    #MODELO
    model=OpenAIChat(id="gpt-4.1-mini"),
    #NOME
    name="Copywriter",

    #MEMORY
    add_history_to_messages=True,
    num_history_runs=10,
    memory=AgentMemory(db=SqliteMemoryDb(table_name="agent_memory", db_file='tmp/memory.db'),
        create_user_memories=True,
        update_user_memories_after_run=True,
        create_session_summary=True,
        update_session_summary_after_run=True,),
    #Armazenamento
    storage=SqliteStorage(table_name="agent_session", db_file="tmp/storage.db"),
    #Ferramentas
    tools=[TavilyTools(),list_available_creators,get_creator_transcriptions],
    #Prompts
    show_tool_calls=True,
    description="Você é um profissional copywriter Senior, e seu nome é Duba.",
    instructions=open("prompts/copywriter.md").read()
)

playground = Playground(
     agents=[
          copywriter
          ],)
app = playground.get_app()

if __name__ == "__main__":
     playground.serve("mk_agent:app", reload=True)