#using serper for google search
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool

# Create search tool using decorator
@tool
def search_web(query: str) -> str:
    """Search the web using Google Serper API.

    Args:
        query: The search query to execute

    Returns:
        Search results from Google
    """
    search = GoogleSerperAPIWrapper()
    return search.run(query)

# Test the search tool
print("Testing search tool:")
print(search_web.invoke("What is the capital of France?"))

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

tools = [search_web]
agent = create_agent(model, tools)

events = agent.stream(
    {
        "messages": [
            ("user", "What is the hometown of the reigning men's U.S. Open champion 2025?")
        ]
    },
    stream_mode="values",
)

for event in events:
    event["messages"][-1].pretty_print()