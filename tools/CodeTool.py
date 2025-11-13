from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import os
import subprocess
import sys
from dotenv import load_dotenv
load_dotenv()

@tool
def run_code(code: str) -> str:
    """Execute Python code and return the result.

    Args:
        code: Python code to execute. Can be a code snippet or a natural language
              description of what code should be run.

    Returns:
        The output from executing the code
    """
    try:
        # If the input looks like natural language, use LLM to generate code
        code_clean = code.strip()
        if not code_clean.startswith(("import", "from", "def", "class", "print", "#", "if", "for", "while", "try")):
            # Likely natural language - generate code using LLM
            model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            prompt = f"""Convert the following request into executable Python code.
Return ONLY the Python code, nothing else. No explanations, no markdown formatting, just the code.

Request: {code}"""
            
            generated_code = model.invoke(prompt).content.strip()
            
            # Remove markdown code blocks if present
            if generated_code.startswith("```"):
                generated_code = generated_code.split("```")[1]
                if generated_code.startswith("python"):
                    generated_code = generated_code[6:]
                generated_code = generated_code.strip()
            
            code_to_execute = generated_code
        else:
            code_to_execute = code_clean
        
        # Execute the code
        result = subprocess.run(
            [sys.executable, "-c", code_to_execute],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                output = "Code executed successfully (no output)."
            return f"Code executed successfully.\n\nOutput:\n{output}"
        else:
            error = result.stderr.strip()
            return f"Error executing code:\n{error}"
            
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (exceeded 30 seconds)."
    except Exception as e:
        return f"Error executing code: {str(e)}"