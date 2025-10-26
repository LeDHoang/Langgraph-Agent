#define langgraph tools and models
from langchain.tools import tool
from langchain.chains import init_chat_model

#define tools
#search the web for the query
@tool
def search_web(query: str) -> str:
    """Search the web for the query"""
    return "I found this information for you: " + query
#document retrieval
@tool
def document_retrieval(query: str) -> str:
    """Retrieve the document for the query"""
    return "I found this document for you: " + query
#sql retrieval
@tool
def sql_retrieval(query: str) -> str:
    """Retrieve the sql for the query"""
    return "I found this sql for you: " + query
#Running code 
@tool
def run_code(code: str) -> str:
    """Run the code and return the result"""
    return "I ran the code and got this result: " + code
#define models
model = init_chat_model(model="gpt-4o-mini", temperature=0)

#define agent
agent = model.bind_tools([search_web, document_retrieval, sql_retrieval, run_code])

#define flow
flow = agent | model