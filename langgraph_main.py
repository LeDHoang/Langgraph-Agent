# LangGraph Agent using official LangChain create_agent pattern
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import os
from dotenv import load_dotenv
load_dotenv()

# Import tools from tools folder
from tools.SearchTool import search_web
from tools.DocumentTool import document_retrieval
from tools.SQLTool import sql_retrieval
from tools.CodeTool import run_code

openai_api_key = os.getenv("OPENAI_API_KEY")

# Define the model
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=openai_api_key
)

# Create agent using official LangChain pattern with automatic tool selection
agent = create_agent(
    model=model,
    tools=[search_web, document_retrieval, sql_retrieval, run_code],
    system_prompt="""You are a helpful assistant with access to various tools. When answering questions, follow this priority order:

1. FIRST: Check document_retrieval tool for information from ingested documents
2. SECOND: Check sql_retrieval tool for information from databases
3. LAST: Only use search_web tool if the information cannot be found in local documents or databases

Always prefer local, authoritative sources (documents and databases) over online search results. Only search the web as a last resort when local sources don't contain the needed information.

Use the code execution tool only when you need to perform calculations, data analysis, or run code - not for information retrieval."""
)

def create_agent_with_tools(tools_list):
    """Create an agent with a specific set of tools."""
    return create_agent(
        model=model,
        tools=tools_list,
        system_prompt="""You are a helpful assistant with access to various tools. When answering questions, follow this priority order:

1. FIRST: Check document_retrieval tool for information from ingested documents (if available)
2. SECOND: Check sql_retrieval tool for information from databases (if available)
3. LAST: Only use search_web tool if the information cannot be found in local documents or databases (if available)

Always prefer local, authoritative sources (documents and databases) over online search results. Only search the web as a last resort when local sources don't contain the needed information.

Use the code execution tool only when you need to perform calculations, data analysis, or run code - not for information retrieval."""
    )

def run_agent_query(query: str, conversation_history: list = None):
    """
    Execute agent query and capture tool usage and execution logs.

    Args:
        query: User query string
        conversation_history: Optional list of previous messages

    Returns:
        tuple: (final_response, tools_used, execution_logs)
    """
    # Prepare messages
    messages = []
    if conversation_history:
        messages.extend(conversation_history)

    # Add current user query
    messages.append(HumanMessage(content=query))

    # Initialize tracking variables
    tools_used = []
    execution_logs = []

    try:
        # Use invoke to get the complete result and analyze execution
        result = agent.invoke({"messages": messages})

        # Extract final response
        final_messages = result["messages"]
        final_response = None
        if final_messages:
            last_message = final_messages[-1]
            if isinstance(last_message, AIMessage):
                final_response = last_message.content

        # Create detailed execution logs by analyzing message flow
        execution_logs.append({
            "type": "execution_overview",
            "step": 1,
            "total_messages": len(final_messages),
            "message_flow": [
                {
                    "index": i,
                    "type": msg.__class__.__name__,
                    "content_length": len(msg.content),
                    "has_tool_calls": bool(getattr(msg, 'tool_calls', None)),
                    "tool_call_count": len(getattr(msg, 'tool_calls', [])) if hasattr(msg, 'tool_calls') else 0
                }
                for i, msg in enumerate(final_messages)
            ]
        })

        # Extract tool usage from messages
        for i, msg in enumerate(final_messages):
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_info = {
                        "tool_name": tool_call["name"],
                        "call_id": tool_call["id"],
                        "arguments": tool_call["args"],
                        "timestamp": getattr(msg, 'timestamp', None),
                        "status": "called"
                    }

                    # Look for corresponding tool response
                    for j in range(i + 1, len(final_messages)):
                        if isinstance(final_messages[j], ToolMessage) and final_messages[j].tool_call_id == tool_call["id"]:
                            tool_info["response"] = final_messages[j].content[:500] + "..." if len(final_messages[j].content) > 500 else final_messages[j].content
                            tool_info["status"] = "completed"
                            break

                    tools_used.append(tool_info)

        return final_response or "No response generated", tools_used, execution_logs

    except Exception as e:
        error_msg = f"Error executing agent query: {str(e)}"
        execution_logs.append({
            "type": "error",
            "step": len(execution_logs) + 1,
            "error": error_msg,
            "timestamp": str(os.times())
        })
        return error_msg, [], execution_logs

def run_agent_query_with_tools(agent_instance, query: str, conversation_history: list = None):
    """
    Execute agent query with a specific agent instance and capture tool usage and execution logs.

    Args:
        agent_instance: The agent to use for the query
        query: User query string
        conversation_history: Optional list of previous messages

    Returns:
        tuple: (final_response, tools_used, execution_logs)
    """
    # Prepare messages
    messages = []
    if conversation_history:
        messages.extend(conversation_history)

    # Add current user query
    messages.append(HumanMessage(content=query))

    # Initialize tracking variables
    tools_used = []
    execution_logs = []

    try:
        # Use invoke to get the complete result and analyze execution
        result = agent_instance.invoke({"messages": messages})

        # Extract final response
        final_messages = result["messages"]
        final_response = None
        if final_messages:
            last_message = final_messages[-1]
            if isinstance(last_message, AIMessage):
                final_response = last_message.content

        # Create detailed execution logs by analyzing message flow
        execution_logs.append({
            "type": "execution_overview",
            "step": 1,
            "total_messages": len(final_messages),
            "message_flow": [
                {
                    "index": i,
                    "type": msg.__class__.__name__,
                    "content_length": len(msg.content),
                    "has_tool_calls": bool(getattr(msg, 'tool_calls', None)),
                    "tool_call_count": len(getattr(msg, 'tool_calls', [])) if hasattr(msg, 'tool_calls') else 0
                }
                for i, msg in enumerate(final_messages)
            ]
        })

        # Extract tool usage from messages
        for i, msg in enumerate(final_messages):
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_info = {
                        "tool_name": tool_call["name"],
                        "call_id": tool_call["id"],
                        "arguments": tool_call["args"],
                        "timestamp": getattr(msg, 'timestamp', None),
                        "status": "called"
                    }

                    # Look for corresponding tool response
                    for j in range(i + 1, len(final_messages)):
                        if isinstance(final_messages[j], ToolMessage) and final_messages[j].tool_call_id == tool_call["id"]:
                            tool_info["response"] = final_messages[j].content[:500] + "..." if len(final_messages[j].content) > 500 else final_messages[j].content
                            tool_info["status"] = "completed"
                            break

                    tools_used.append(tool_info)

        return final_response or "No response generated", tools_used, execution_logs

    except Exception as e:
        error_msg = f"Error executing agent query: {str(e)}"
        execution_logs.append({
            "type": "error",
            "step": len(execution_logs) + 1,
            "error": error_msg,
            "timestamp": str(os.times())
        })
        return error_msg, [], execution_logs

# Example usage:
if __name__ == "__main__":
    # Test the new agent
    query = "Search for information about Python programming function print()"
    print(f"Testing query: {query}")

    response, tools_used, execution_logs = run_agent_query(query)

    print("\n=== Response ===")
    print(response)

    print("\n=== Tools Used ===")
    for tool in tools_used:
        print(f"- {tool['tool_name']}: {tool['status']}")

    print(f"\n=== Execution Logs ===")
    print(f"Captured {len(execution_logs)} log entries")