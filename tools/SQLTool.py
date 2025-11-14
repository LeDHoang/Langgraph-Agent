import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import pathlib

# Import config functions - handle both direct execution and module import
try:
    from .config import is_database_enabled
except ImportError:
    # If running as script, import directly
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import is_database_enabled

# Initialize database connections (lazy loading)
_databases = {}

def _get_database(db_name="chinook"):
    """Initialize and return the SQL database connection.

    Args:
        db_name: Name of the database to connect to ('chinook', 'employees', 'projects')

    Returns:
        SQLDatabase connection object
    """
    if db_name in _databases:
        return _databases[db_name]

    # Map database names to file paths
    db_paths = {
        "chinook": "Chinook.db",
        "employees": "database/softwareone_employees.db",
        "projects": "database/softwareone_projects.db"
    }

    if db_name not in db_paths:
        available_dbs = list(db_paths.keys())
        raise ValueError(f"Unknown database '{db_name}'. Available databases: {available_dbs}")

    db_path = pathlib.Path(db_paths[db_name])
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database file {db_path} not found. Please ensure the database exists."
        )

    _databases[db_name] = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    return _databases[db_name]

@tool
def sql_retrieval(query: str, database: str = "chinook") -> str:
    """Execute a SQL query on the specified database and return results.

    Only enabled databases can be accessed.

    Args:
        query: A natural language question or SQL query to execute on the database.
               If a natural language question is provided, the tool will attempt to
               convert it to SQL and execute it.
        database: Database to query ('chinook', 'employees', 'projects').
                 Defaults to 'chinook' for backward compatibility.

    Returns:
        The results from the SQL query execution
    """
    # Check if database is enabled
    if not is_database_enabled(database):
        return f"Database '{database}' is not enabled for access. Please enable it in the file management panel."

    try:
        db = _get_database(database)
        
        # If the query looks like a SQL statement, execute it directly
        query_upper = query.strip().upper()
        if query_upper.startswith(("SELECT", "WITH")):
            # Direct SQL query
            result = db.run(query)
            return f"Query executed successfully. Results:\n{result}"
        else:
            # Natural language query - use LLM to generate SQL
            model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Get database schema information
            tables = db.get_usable_table_names()
            schema_info = ""
            for table in tables[:5]:  # Limit to first 5 tables for context
                schema_info += f"\n{table}:\n{db.get_table_info_no_throw([table])}\n"
            
            # Generate SQL query from natural language
            prompt = f"""Given the following database schema:
{schema_info}

Convert the following question into a SQL query: {query}

Return ONLY the SQL query, nothing else. Do not include explanations or markdown formatting."""
            
            sql_query = model.invoke(prompt).content.strip()
            
            # Remove markdown code blocks if present
            if sql_query.startswith("```"):
                sql_query = sql_query.split("```")[1]
                if sql_query.startswith("sql"):
                    sql_query = sql_query[3:]
                sql_query = sql_query.strip()
            
            # Execute the generated SQL query
            result = db.run(sql_query)
            return f"Generated SQL: {sql_query}\n\nResults:\n{result}"
            
    except Exception as e:
        return f"Error executing SQL query: {str(e)}"