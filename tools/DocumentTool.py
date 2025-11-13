from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize vector store (will be populated on first use)
vector_store = None

def _initialize_vector_store():
    """Initialize the vector store with documents from the docs folder."""
    global vector_store
    if vector_store is not None:
        return vector_store
    
    # Load documents from PDF files in docs folder
    import glob
    pdf_files = glob.glob("docs/*.pdf")
    
    if not pdf_files:
        # If no PDFs found, create empty vector store
        vector_store = InMemoryVectorStore(embeddings)
        return vector_store
    
    all_docs = []
    for file_path in pdf_files:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        all_docs.extend(docs)
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(all_docs)
    
    # Create and populate vector store
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(all_splits)
    
    return vector_store

@tool
def document_retrieval(query: str) -> str:
    """Retrieve relevant documents from the document store based on a query.

    Args:
        query: The search query to find relevant documents

    Returns:
        Retrieved document content relevant to the query
    """
    # Initialize vector store if needed
    store = _initialize_vector_store()
    
    # Perform similarity search
    results = store.similarity_search(query, k=3)
    
    if not results:
        return "No relevant documents found."
    
    # Combine results into a single string
    retrieved_content = "\n\n".join([
        f"Document {i+1}:\n{result.page_content[:500]}..." 
        for i, result in enumerate(results)
    ])
    
    return retrieved_content