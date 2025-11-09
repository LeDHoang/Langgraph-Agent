from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# Create the model with OpenAI Code Interpreter
model = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Bind OpenAI's built-in code interpreter tool
model_with_code_interpreter = model.bind_tools(
    [
        {
            "type": "code_interpreter",
            # Create a new container for each execution
            "container": {"type": "auto"},
        }
    ]
)

# Test the tool
if __name__ == "__main__":
    # Test with the model using OpenAI Code Interpreter
    response = model_with_code_interpreter.invoke(
        "Write and run code to answer the question: Calculate the sum of the first 1000 prime numbers?"
    )
    print(f"OpenAI Code Interpreter response: {response}")

    # Show tool calls if any
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"Tool calls: {response.tool_calls}")

    # Extract and display the generated code and results
    if response.content and isinstance(response.content, list):
        for item in response.content:
            if item.get('type') == 'code_interpreter_call':
                print(f"\OpenAI Code Interpreter Generated Code:")
                print(f"Container ID: {item.get('container_id')}")
                print(f"Status: {item.get('status')}")
                print(f"Code:\n{item.get('code')}")
                print("-" * 50)
            elif item.get('type') == 'text':
                print(f"OpenAI Code Interpreter Result: {item.get('text')}")
    print("-" * 50)
    # The response will contain the results from OpenAI's code interpreter
    print(f"Final answer: {response.content}")