from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
import os
from pathlib import Path
from dotenv import load_dotenv

# Import config functions - handle both direct execution and module import
try:
    from .config import is_document_enabled, get_enabled_documents
except ImportError:
    # If running as script, import directly
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import is_document_enabled, get_enabled_documents

load_dotenv()

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize vector store (will be loaded from disk or created on first use)
vector_store = None

def _initialize_vector_store():
    """Initialize the vector store from FAISS index on disk, or create empty store if not found."""
    global vector_store
    if vector_store is not None:
        return vector_store

    # Check if FAISS index exists on disk
    faiss_index_path = Path("faiss_index")
    if faiss_index_path.exists() and faiss_index_path.is_dir():
        try:
            # Load existing FAISS index
            vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            print(f"✅ Loaded FAISS index with {vector_store.index.ntotal} documents")
            return vector_store
        except Exception as e:
            print(f"⚠️  Failed to load existing FAISS index: {e}")

    # If no index exists or loading failed, create empty vector store
    print("ℹ️  No FAISS index found, creating empty vector store")
    vector_store = FAISS.from_texts([""], embeddings)  # Create empty FAISS index
    return vector_store

def refresh_vector_store():
    """Refresh the vector store by reloading from disk after ingestion."""
    global vector_store
    vector_store = None  # Reset to force reload
    return _initialize_vector_store()

@tool
def document_retrieval(query: str) -> str:
    """Retrieve relevant documents from the document store based on a query.

    Only documents that are enabled in the configuration will be searched.

    Args:
        query: The search query to find relevant documents

    Returns:
        Retrieved document content relevant to the query
    """
    # Initialize vector store if needed
    store = _initialize_vector_store()

    # Check if we have any documents in the index
    try:
        doc_count = store.index.ntotal if hasattr(store, 'index') else 0
        if doc_count == 0:
            return "No documents have been ingested yet. Please run the document ingestion process first."
    except:
        return "Document store is not properly initialized. Please run the document ingestion process."

    # Get enabled documents
    enabled_docs = get_enabled_documents()
    if not enabled_docs:
        return "No documents are currently enabled for searching. Please enable documents in the file management panel."

    # Perform similarity search
    try:
        # Get more results than needed to account for filtering
        raw_results = store.similarity_search(query, k=10)
    except Exception as e:
        return f"Error performing document search: {str(e)}"

    if not raw_results:
        return f"No relevant documents found for query: '{query}'"

    # Filter results based on enabled documents
    filtered_results = []
    for result in raw_results:
        source = result.metadata.get('source', '')
        if source:
            # Extract filename from path
            filename = Path(source).name
            if filename in enabled_docs:
                filtered_results.append(result)

        # Stop when we have enough results
        if len(filtered_results) >= 3:
            break

    if not filtered_results:
        return f"No results found in enabled documents for query: '{query}'. Try enabling more documents or check the query."

    # Combine results into a single string
    retrieved_content = f"Found {len(filtered_results)} relevant document sections from enabled sources:\n\n"
    retrieved_content += "\n\n".join([
        f"📄 Section {i+1}:\n{result.page_content[:800]}..." +
        (f"\n📍 Source: {Path(result.metadata.get('source', 'Unknown')).name}" if result.metadata.get('source') else "")
        for i, result in enumerate(filtered_results)
    ])

    return retrieved_content