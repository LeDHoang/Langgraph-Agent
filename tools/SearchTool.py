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