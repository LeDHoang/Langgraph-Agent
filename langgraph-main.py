#define langgraph tools and models
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from typing import TypedDict, List, Annotated, Literal
import operator
from langchain_core.messages import AnyMessage
import os
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

#define the agent/messages state
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
    question: str #the question the user asked
    chat_history: List[tuple] #the chat history
    generation: str #the generation of the answer from the model
    tool_choice: str #the tool choice from the model
    tool_output: str #the output of the tool
   
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

#define edges
#entry point - router
#Conditional edge - read tool_choice from state and route to the appropriate tool
#if tool_choice is not found, route to end
#normal edge - tool output to generate final answer
#end point - generate final answer

#define nodes (tool execution nodes)
def router_decision(state: MessagesState) -> Literal["search_web", "document_retrieval", "sql_retrieval", "run_code", "generate_final_answer"]:
    #selecting tools call based on tool_choice
    tool_choice = state.get("tool_choice", "")
    if tool_choice == "search_web":
        return "search_web"
    elif tool_choice == "document_retrieval":
        return "document_retrieval"
    elif tool_choice == "sql_retrieval":
        return "sql_retrieval"
    elif tool_choice == "run_code":
        return "run_code"
    else:
        return "generate_final_answer"


#run_rag_tool 
def run_rag_tool(state: MessagesState) -> MessagesState:
    #call tool document retrieval
    # document_retrieval.invoke(state["question"])
    #update state with tool output
    state["tool_output"] = document_retrieval.invoke(state["question"])
    return state
#run_search_tool
def run_search_tool(state: MessagesState) -> MessagesState:
    #call tool search web
    search_web.invoke(state["question"])
    #update state with tool output
    state["tool_output"] = search_web.invoke(state["question"])
    return state
#run_sql_tool
def run_sql_tool(state: MessagesState) -> MessagesState:
    #call tool sql retrieval
    sql_retrieval.invoke(state["question"])
    #update state with tool output
    state["tool_output"] = sql_retrieval.invoke(state["question"])
    return state
#run_code_tool
def run_code_tool(state: MessagesState) -> MessagesState:
    #call tool run code
    run_code.invoke(state["question"])
    #update state with tool output
    state["tool_output"] = run_code.invoke(state["question"])
    return state
#generate final answer
def generate_final_answer(state: MessagesState) -> MessagesState:
    #generate final answer from model with question and tool output
    final_answer = model.invoke(state["question"] + " " + state["tool_output"])
    #update state with final answer
    state["generation"] = final_answer
    return state

#define models first (needed for generate_final_answer)
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=openai_api_key
)

#define agent (bind tools to model)
agent = model.bind_tools([search_web, document_retrieval, sql_retrieval, run_code])

#define graph
graph = StateGraph(MessagesState)

# Add all nodes to the graph
graph.add_node("search_web", run_search_tool)
graph.add_node("document_retrieval", run_rag_tool)
graph.add_node("sql_retrieval", run_sql_tool)
graph.add_node("run_code", run_code_tool)
graph.add_node("generate_final_answer", generate_final_answer)

# Add conditional edges from START (entry point) to tool nodes
graph.add_conditional_edges(
    "__start__",
    router_decision,
    {
        "search_web": "search_web",
        "document_retrieval": "document_retrieval",
        "sql_retrieval": "sql_retrieval",
        "run_code": "run_code",
        "generate_final_answer": "generate_final_answer"
    }
)

# Add edges from tool nodes to final answer generation
graph.add_edge("search_web", "generate_final_answer")
graph.add_edge("document_retrieval", "generate_final_answer")
graph.add_edge("sql_retrieval", "generate_final_answer")
graph.add_edge("run_code", "generate_final_answer")

# Compile the graph
app = graph.compile()

# Example usage:
if __name__ == "__main__":
    # Initial state
    initial_state = {
        "messages": [],
        "llm_calls": 0,
        "question": "Search for information about Python programming function print()",
        "chat_history": [],
        "generation": "",
        "tool_choice": "search_web",  # This will route to search_web tool
        "tool_output": ""
    }

    # Run the graph
    result = app.invoke(initial_state)
    print("Full result:", result)
    print("Final result:", result["generation"].content)