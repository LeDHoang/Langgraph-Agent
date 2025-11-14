#!/usr/bin/env python3
"""
Document and Database Ingestion Script

This script ingests documents from the docs/ folder and prepares databases for querying.
It creates a persistent FAISS vector store for document retrieval and validates database connections.
"""

import os
import sys
import glob
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LangChain components
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.utilities.sql_database import SQLDatabase

# Import config functions - handle both direct execution and module import
try:
    from .config import update_enabled_documents, update_enabled_databases
except ImportError:
    # If running as script, import directly
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import update_enabled_documents, update_enabled_databases

def ingest_documents(pdf_files):
    """Ingest documents from docs folder and create FAISS index."""
    print("🔍 Scanning docs folder for PDF files...")

    if not pdf_files:
        print("⚠️  No PDF files found in docs/ folder")
        return False

    print(f"📄 Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"  - {os.path.basename(pdf_file)}")

    # Load documents from all PDFs
    print("\n📖 Loading documents...")
    all_docs = []
    for file_path in pdf_files:
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            # Add source metadata to each document
            for doc in docs:
                doc.metadata["source"] = file_path
            all_docs.extend(docs)
            print(f"  ✅ Loaded {len(docs)} pages from {os.path.basename(file_path)}")
        except Exception as e:
            print(f"  ❌ Error loading {os.path.basename(file_path)}: {e}")

    if not all_docs:
        print("❌ No documents could be loaded")
        return False

    print(f"\n📄 Total documents loaded: {len(all_docs)}")

    # Split documents into chunks
    print("\n✂️  Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(all_docs)
    print(f"  📏 Created {len(chunks)} text chunks")

    # Create embeddings
    print("\n🧠 Creating embeddings...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create FAISS index
    print("💾 Creating FAISS vector store...")
    faiss_index = FAISS.from_documents(chunks, embeddings)

    # Save the index
    faiss_index.save_local("faiss_index")
    print("  ✅ FAISS index saved to faiss_index/ folder")

    return True

def validate_databases():
    """Validate database connections and schemas."""
    print("\n🗄️  Validating database connections...")

    # Database configuration
    db_configs = {
        "chinook": "Chinook.db",
        "employees": "database/softwareone_employees.db",
        "projects": "database/softwareone_projects.db"
    }

    for db_name, db_path in db_configs.items():
        try:
            if not Path(db_path).exists():
                print(f"  ⚠️  Database {db_name} not found at {db_path}")
                continue

            # Connect to database
            db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

            # Get basic info
            tables = db.get_usable_table_names()
            print(f"  ✅ {db_name}: {len(tables)} tables available")

            # Show first few tables
            for table in tables[:3]:
                try:
                    info = db.get_table_info_no_throw([table])
                    print(f"    📊 {table}")
                except:
                    pass

        except Exception as e:
            print(f"  ❌ Error connecting to {db_name}: {e}")

def main():
    """Main ingestion function."""
    print("🚀 Starting document and database ingestion...\n")

    # Get PDF files first
    pdf_files = glob.glob("docs/*.pdf")

    # Ingest documents
    docs_success = ingest_documents(pdf_files)

    # Validate databases
    validate_databases()

    if docs_success:
        # Update configuration with all available documents and databases
        try:
            # Get all document filenames
            all_docs = [os.path.basename(pdf) for pdf in pdf_files]
            update_enabled_documents(all_docs)
            print(f"✅ Updated configuration with {len(all_docs)} documents")

            # Get all available databases
            all_dbs = ["chinook", "employees", "projects"]
            update_enabled_databases(all_dbs)
            print(f"✅ Updated configuration with {len(all_dbs)} databases")

        except Exception as config_error:
            print(f"⚠️  Configuration update failed: {config_error}")

        print("\n🎉 Ingestion completed successfully!")
        print("📚 Documents are now available for querying")
        print("🗄️  Databases are ready for SQL queries")
        return True
    else:
        print("\n❌ Ingestion completed with issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)