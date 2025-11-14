"""
Configuration module for managing access to documents and databases.

This module provides a centralized way to manage which documents and databases
are accessible to the AI agent tools.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set

# Configuration file path
CONFIG_FILE = Path("tools/config.json")

# Default configuration
DEFAULT_CONFIG = {
    "enabled_documents": [],
    "enabled_databases": [],
    "document_sources": {},  # Maps document names to their source files
    "database_mappings": {   # Maps database names to their file paths
        "chinook": "Chinook.db",
        "employees": "database/softwareone_employees.db",
        "projects": "database/softwareone_projects.db"
    }
}

def load_config() -> Dict:
    """Load configuration from file or return defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict) -> None:
    """Save configuration to file."""
    try:
        CONFIG_FILE.parent.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save config file: {e}")

def update_enabled_documents(enabled_docs: List[str]) -> None:
    """Update the list of enabled documents."""
    config = load_config()
    config["enabled_documents"] = enabled_docs
    save_config(config)

def update_enabled_databases(enabled_dbs: List[str]) -> None:
    """Update the list of enabled databases."""
    config = load_config()
    config["enabled_databases"] = enabled_dbs
    save_config(config)

def is_document_enabled(doc_name: str) -> bool:
    """Check if a document is enabled."""
    config = load_config()
    return doc_name in config["enabled_documents"]

def is_database_enabled(db_name: str) -> bool:
    """Check if a database is enabled."""
    config = load_config()
    return db_name in config["enabled_databases"]

def get_enabled_documents() -> List[str]:
    """Get list of enabled documents."""
    config = load_config()
    return config["enabled_documents"]

def get_enabled_databases() -> List[str]:
    """Get list of enabled databases."""
    config = load_config()
    return config["enabled_databases"]

def get_database_path(db_name: str) -> str:
    """Get the file path for a database."""
    config = load_config()
    return config["database_mappings"].get(db_name)

def get_all_databases() -> Dict[str, str]:
    """Get all available databases and their paths."""
    config = load_config()
    return config["database_mappings"]

# Initialize with defaults if config doesn't exist
if not CONFIG_FILE.exists():
    save_config(DEFAULT_CONFIG)
