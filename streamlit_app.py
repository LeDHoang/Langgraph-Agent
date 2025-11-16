import json
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
import subprocess
from pathlib import Path
from tools.config import update_enabled_documents, update_enabled_databases

LOGS_DIR = Path("logs")

# Page configuration
st.set_page_config(
    page_title="LangGraph Agent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    section[data-testid="stSidebar"] > div:first-child .sidebar-spacer {
        flex-grow: 1;
    }
    section[data-testid="stSidebar"] > div:first-child .sidebar-nav button {
        width: 100%;
        justify-content: center;
    }
    section[data-testid="stSidebar"] > div:first-child .sidebar-nav button + button {
        margin-top: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "conversation_counter" not in st.session_state:
    st.session_state.conversation_counter = 1

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if "logs_loaded" not in st.session_state:
    st.session_state.logs_loaded = False

# Initialize file management session state
if "file_window_expanded" not in st.session_state:
    st.session_state.file_window_expanded = False

if "file_toggles" not in st.session_state:
    st.session_state.file_toggles = {}

if "ingestion_status" not in st.session_state:
    st.session_state.ingestion_status = None

# Initialize tool management session state
if "tool_toggles" not in st.session_state:
    st.session_state.tool_toggles = {
        "search_web": True,
        "document_retrieval": True,
        "sql_retrieval": True,
        "run_code": True
    }

def create_new_conversation():
    """Create a new conversation and return its ID."""
    conv_id = f"conv_{st.session_state.conversation_counter}"
    st.session_state.conversations[conv_id] = {
        "messages": [],
        "tools_used": [],
        "execution_logs": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.conversation_counter += 1
    save_conversation(conv_id)
    return conv_id

def get_current_conversation():
    """Get the current conversation data."""
    conv_id = st.session_state.current_conversation_id
    if conv_id and conv_id in st.session_state.conversations:
        return st.session_state.conversations[conv_id]
    return None

def update_current_conversation(messages=None, tools_used=None, execution_logs=None):
    """Update the current conversation with new data."""
    conv_id = st.session_state.current_conversation_id
    if conv_id and conv_id in st.session_state.conversations:
        if messages is not None:
            st.session_state.conversations[conv_id]["messages"] = messages
        if tools_used is not None:
            st.session_state.conversations[conv_id]["tools_used"] = tools_used
        if execution_logs is not None:
            st.session_state.conversations[conv_id]["execution_logs"] = execution_logs
        save_conversation(conv_id)

def get_docs_files():
    """Get all files from the docs directory."""
    docs_path = Path("docs")
    if docs_path.exists():
        return [f.name for f in docs_path.iterdir() if f.is_file()]
    return []

def get_database_files():
    """Get all files from the database directory."""
    db_path = Path("database")
    if db_path.exists():
        return [f.name for f in db_path.iterdir() if f.is_file()]
    return []

def ingest_documents():
    """Run the document ingestion script."""
    try:
        # Run the ingestion script
        result = subprocess.run(
            ["python", "tools/ingests_docs.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            # Refresh the vector store in DocumentTool after successful ingestion
            try:
                from tools.DocumentTool import refresh_vector_store
                refresh_vector_store()
                print("✅ Vector store refreshed after ingestion")
            except Exception as refresh_error:
                print(f"⚠️  Vector store refresh failed: {refresh_error}")
                # Don't fail the whole process if refresh fails

            return "✅ Documents and databases ingested successfully!"
        else:
            return f"❌ Ingestion failed: {result.stderr}"
    except Exception as e:
        return f"❌ Error during ingestion: {str(e)}"

def get_enabled_tools():
    """Get the list of enabled tools based on toggle states."""
    enabled_tools = []
    tool_configs = {
        "search_web": ("Search Web", "🔍"),
        "document_retrieval": ("Document Retrieval", "📄"),
        "sql_retrieval": ("SQL Query", "🗄️"),
        "run_code": ("Code Execution", "💻")
    }

    for tool_name, (display_name, icon) in tool_configs.items():
        if st.session_state.tool_toggles.get(tool_name, True):
            enabled_tools.append({
                "name": tool_name,
                "display_name": display_name,
                "icon": icon
            })

    return enabled_tools

def get_enabled_tool_functions():
    """Get the actual tool functions that are enabled."""
    from tools.SearchTool import search_web
    from tools.DocumentTool import document_retrieval
    from tools.SQLTool import sql_retrieval
    from tools.CodeTool import run_code

    tool_functions = {
        "search_web": search_web,
        "document_retrieval": document_retrieval,
        "sql_retrieval": sql_retrieval,
        "run_code": run_code
    }

    enabled_functions = []
    for tool_name in st.session_state.tool_toggles:
        if st.session_state.tool_toggles[tool_name]:
            enabled_functions.append(tool_functions[tool_name])

    return enabled_functions


def ensure_logs_dir():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def conversation_log_path(conv_id: str) -> Path:
    return LOGS_DIR / f"{conv_id}.json"


def serialize_message(message):
    if isinstance(message, HumanMessage):
        msg_type = "human"
    elif isinstance(message, AIMessage):
        msg_type = "ai"
    elif isinstance(message, SystemMessage):
        msg_type = "system"
    else:
        msg_type = getattr(message, "type", "system")

    content = getattr(message, "content", str(message))
    return {"type": msg_type, "content": content}


def deserialize_message(message_data):
    msg_type = message_data.get("type")
    content = message_data.get("content", "")

    if msg_type == "human":
        return HumanMessage(content=content)
    if msg_type == "ai":
        return AIMessage(content=content)
    return SystemMessage(content=content)


def serialize_conversation(conv_id: str, conversation: dict) -> dict:
    return {
        "conversation_id": conv_id,
        "created_at": conversation.get("created_at"),
        "messages": [serialize_message(msg) for msg in conversation.get("messages", [])],
        "tools_used": conversation.get("tools_used", []),
        "execution_logs": conversation.get("execution_logs", []),
    }


def save_conversation(conv_id: str):
    conversation = st.session_state.conversations.get(conv_id)
    if not conversation:
        return

    ensure_logs_dir()
    payload = serialize_conversation(conv_id, conversation)
    try:
        with conversation_log_path(conv_id).open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
    except OSError:
        pass


def delete_conversation_log(conv_id: str):
    try:
        path = conversation_log_path(conv_id)
        if path.exists():
            path.unlink()
    except OSError:
        pass


def load_conversations_from_disk() -> dict:
    ensure_logs_dir()
    conversations = {}
    for file_path in LOGS_DIR.glob("*.json"):
        try:
            with file_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        conv_id = payload.get("conversation_id")
        if not conv_id:
            continue

        messages = [
            deserialize_message(msg_data) for msg_data in payload.get("messages", [])
        ]

        conversations[conv_id] = {
            "messages": messages,
            "tools_used": payload.get("tools_used", []),
            "execution_logs": payload.get("execution_logs", []),
            "created_at": payload.get(
                "created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
        }

    return conversations


def load_conversations_into_session():
    loaded = load_conversations_from_disk()
    if not loaded:
        return

    st.session_state.conversations.update(loaded)

    numeric_ids = []
    for conv_id in loaded:
        try:
            numeric_ids.append(int(conv_id.split("_")[1]))
        except (IndexError, ValueError):
            continue

    if numeric_ids:
        st.session_state.conversation_counter = max(
            st.session_state.conversation_counter, max(numeric_ids) + 1
        )

    if st.session_state.current_conversation_id is None:
        sorted_convs = sorted(
            loaded.items(),
            key=lambda x: x[1].get("created_at", ""),
            reverse=True,
        )
        if sorted_convs:
            st.session_state.current_conversation_id = sorted_convs[0][0]


def build_log_signature(log_entry) -> str:
    try:
        return json.dumps(log_entry, sort_keys=True, default=str)
    except TypeError:
        return str(log_entry)


def summarize_text(text: str, max_length: int = 60) -> str:
    if text is None:
        return "<empty>"
    trimmed = text.strip()
    if not trimmed:
        return "<empty>"
    if len(trimmed) <= max_length:
        return trimmed
    return trimmed[: max_length - 3] + "..."


def get_conversation_title(conv_data: dict, max_length: int = 60) -> str:
    for message in conv_data.get("messages", []):
        if isinstance(message, HumanMessage):
            return summarize_text(message.content, max_length=max_length)
    return "<empty>"

# Load persisted conversations on startup
if not st.session_state.logs_loaded:
    load_conversations_into_session()
    st.session_state.logs_loaded = True

# Sidebar for conversation management
with st.sidebar:
    st.title("💬 Conversations")

    # New conversation button
    if st.button("➕ New Conversation", type="primary"):
        new_conv_id = create_new_conversation()
        st.session_state.current_conversation_id = new_conv_id
        st.rerun()

    st.divider()

    # Conversation list
    if st.session_state.conversations:
        st.subheader("Recent Conversations")

        # Sort conversations by creation time (newest first)
        sorted_convs = sorted(
            st.session_state.conversations.items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        )

        for conv_id, conv_data in sorted_convs:
            # Create a button for each conversation
            conversation_title = get_conversation_title(conv_data, max_length=60)
            button_label = conversation_title
            created_time = conv_data["created_at"]

            # Use columns for better layout
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"{button_label}\n{created_time}", key=f"conv_{conv_id}"):
                    st.session_state.current_conversation_id = conv_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{conv_id}", help="Delete conversation"):
                    del st.session_state.conversations[conv_id]
                    delete_conversation_log(conv_id)
                    if st.session_state.current_conversation_id == conv_id:
                        # If we deleted the current conversation, select another one or create new
                        remaining_convs = list(st.session_state.conversations.keys())
                        if remaining_convs:
                            st.session_state.current_conversation_id = remaining_convs[0]
                        else:
                            st.session_state.current_conversation_id = None
                    st.rerun()

            # Show message count
            msg_count = len(conv_data["messages"])
            tool_count = len(conv_data["tools_used"])
            st.caption(f"💬 {msg_count} messages • 🔧 {tool_count} tools")

    else:
        st.info("No conversations yet. Create a new one to get started!")

    st.markdown("<div class='sidebar-spacer'></div>", unsafe_allow_html=True)

    nav_container = st.container()
    with nav_container:
        st.markdown("<div class='sidebar-nav'>", unsafe_allow_html=True)
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
            st.session_state.current_page = "settings"
            st.rerun()
        if st.button("🧾 Logs", key="nav_logs", use_container_width=True):
            st.session_state.current_page = "logs"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Main content area
current_page = st.session_state.current_page

# Collapsible File Window
if current_page == "home":
    st.title("🤖 LangGraph Agent Chat")

    with st.expander("📁 Document & Database Files", expanded=st.session_state.file_window_expanded):
        doc_col, db_col = st.columns(2)

        with doc_col:
            st.subheader("📄 Documents")
            docs_files = get_docs_files()
            enabled_docs = []
            if docs_files:
                for file in docs_files:
                    file_key = f"docs_{file}"
                    if file_key not in st.session_state.file_toggles:
                        st.session_state.file_toggles[file_key] = True

                    checked = st.checkbox(
                        f"📄 {file}",
                        value=st.session_state.file_toggles[file_key],
                        key=file_key,
                        help=f"Toggle {file} for agent access"
                    )
                    st.session_state.file_toggles[file_key] = checked
                    if checked:
                        enabled_docs.append(file)
            else:
                st.info("No documents found in docs/ directory")

            update_enabled_documents(enabled_docs)

        with db_col:
            st.subheader("🗄️ Databases")
            db_files = get_database_files()
            enabled_dbs = []
            if db_files:
                for file in db_files:
                    file_key = f"db_{file}"
                    if file_key not in st.session_state.file_toggles:
                        st.session_state.file_toggles[file_key] = True

                    checked = st.checkbox(
                        f"🗄️ {file}",
                        value=st.session_state.file_toggles[file_key],
                        key=file_key,
                        help=f"Toggle {file} for agent access"
                    )
                    st.session_state.file_toggles[file_key] = checked
                    if checked:
                        if "employees" in file:
                            enabled_dbs.append("employees")
                        elif "projects" in file:
                            enabled_dbs.append("projects")
                        else:
                            enabled_dbs.append("chinook")
            else:
                st.info("No database files found in database/ directory")

            update_enabled_databases(enabled_dbs)

        st.markdown("<h3 style='text-align: center;'>Actions</h3>", unsafe_allow_html=True)
        action_cols = st.columns([1, 1, 1])
        with action_cols[1]:
            if st.button(
                "🔄 Re-ingest Documents",
                type="primary",
                help="Re-run document ingestion to update the knowledge base",
                use_container_width=True,
            ):
                with st.spinner("Ingesting documents..."):
                    status = ingest_documents()
                    st.session_state.ingestion_status = status
                    st.success(status)
                    st.rerun()

            if st.session_state.ingestion_status:
                if "✅" in st.session_state.ingestion_status:
                    st.success(st.session_state.ingestion_status)
                else:
                    st.error(st.session_state.ingestion_status)

# Ensure we have a current conversation
if st.session_state.current_conversation_id is None and st.session_state.conversations:
    # Auto-select the most recent conversation
    sorted_convs = sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1]["created_at"],
        reverse=True
    )
    st.session_state.current_conversation_id = sorted_convs[0][0]

if st.session_state.current_conversation_id is None:
    # Create first conversation
    new_conv_id = create_new_conversation()
    st.session_state.current_conversation_id = new_conv_id

current_conv = get_current_conversation()
if not current_conv:
    st.error("No conversation selected. Please create a new conversation.")
    st.stop()

if current_page == "home":
    st.subheader("Chat")

    chat_container = st.container()

    with chat_container:
        for message in current_conv["messages"]:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)
            else:
                with st.chat_message("system"):
                    st.write(f"System: {message.content}")

    enabled_tools_for_priority = get_enabled_tools()
    if enabled_tools_for_priority:
        priority_tools = [
            t for t in enabled_tools_for_priority if t["name"] in ["document_retrieval", "sql_retrieval", "search_web"]
        ]

        priority_order = {
            "document_retrieval": 1,
            "sql_retrieval": 2,
            "search_web": 3
        }
        priority_tools.sort(key=lambda x: priority_order.get(x["name"], 4))

        if priority_tools:
            priority_text = " → ".join([f"{t['icon']} {t['display_name']}" for t in priority_tools])
            st.caption(f"🔄 **Search Priority:** {priority_text}")

    if prompt := st.chat_input("Ask the LangGraph agent anything..."):
        user_message = HumanMessage(content=prompt)
        current_conv["messages"].append(user_message)
        update_current_conversation(messages=current_conv["messages"])

        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)

        query_start_time = datetime.now()
        execution_logs = []
        new_tools_used = []
        response = ""
        ai_message = None

        existing_tools = list(current_conv.get("tools_used", []))
        existing_logs = list(current_conv.get("execution_logs", []))

        with st.spinner("🤖 Agent is thinking..."):
            try:
                enabled_tool_functions = get_enabled_tool_functions()

                if not enabled_tool_functions:
                    response = "No tools are enabled. Please enable at least one tool in the Tool Management section."
                    ai_message = AIMessage(content=response)
                    current_conv["messages"].append(ai_message)
                    execution_logs = [{"type": "error", "message": "No tools enabled"}]
                    new_tools_used = []
                else:
                    from langgraph_main import create_agent_with_tools, run_agent_query_with_tools

                    agent = create_agent_with_tools(enabled_tool_functions)
                    response, new_tools_used, execution_logs = run_agent_query_with_tools(agent, prompt)
                    execution_logs = execution_logs or []
                    new_tools_used = new_tools_used or []
                    ai_message = AIMessage(content=response)
                    current_conv["messages"].append(ai_message)

            except Exception as e:
                response = f"Error: {str(e)}"
                ai_message = AIMessage(content=response)
                current_conv["messages"].append(ai_message)
                new_tools_used = []
                execution_logs = [{"type": "error", "message": str(e)}]

        query_end_time = datetime.now()
        duration_seconds = (query_end_time - query_start_time).total_seconds()
        timing_entry = {
            "type": "query_timing",
            "query": prompt,
            "timestamp": query_start_time.isoformat(),
            "start_time": query_start_time.isoformat(),
            "end_time": query_end_time.isoformat(),
            "duration_seconds": round(duration_seconds, 3),
            "tools_used": [
                tool.get("tool_name") for tool in new_tools_used if isinstance(tool, dict)
            ],
        }
        execution_logs = execution_logs or []
        execution_logs.append(timing_entry)

        existing_log_signatures = {build_log_signature(log_entry) for log_entry in existing_logs}
        filtered_new_logs = []
        for log_entry in execution_logs:
            signature = build_log_signature(log_entry)
            if signature not in existing_log_signatures:
                filtered_new_logs.append(log_entry)
                existing_log_signatures.add(signature)
        combined_logs = existing_logs + filtered_new_logs

        existing_tool_ids = {
            tool.get("call_id")
            for tool in existing_tools
            if isinstance(tool, dict) and tool.get("call_id")
        }
        filtered_new_tools = []
        for tool in new_tools_used:
            if not isinstance(tool, dict):
                continue
            call_id = tool.get("call_id")
            if call_id and call_id in existing_tool_ids:
                continue
            if call_id:
                existing_tool_ids.add(call_id)
            if not tool.get("timestamp"):
                tool["timestamp"] = datetime.now().isoformat()
            filtered_new_tools.append(tool)
        combined_tools = existing_tools + filtered_new_tools

        current_conv["tools_used"] = combined_tools
        current_conv["execution_logs"] = combined_logs
        update_current_conversation(
            messages=current_conv["messages"],
            tools_used=combined_tools,
            execution_logs=combined_logs
        )

        assistant_reply = ai_message.content if ai_message else response

        with chat_container:
            with st.chat_message("assistant"):
                st.write(assistant_reply)

        st.rerun()

elif current_page == "settings":
    st.title("⚙️ Settings & Tools")
    st.subheader("🛠️ Tool Management")

    with st.expander("⚙️ Enable/Disable Tools", expanded=False):
        st.write(
            "Control which tools are available to the agent. Disabled tools will not be accessible during conversations."
        )
        st.info(
            "📋 **Tool Priority Order:** 1️⃣ Documents → 2️⃣ Databases → 3️⃣ Web Search "
            "(only when local sources don't have the information)"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔍 Web Search")
            search_enabled = st.checkbox(
                "Enable Web Search Tool",
                value=st.session_state.tool_toggles["search_web"],
                key="toggle_search_web",
                help="Allow the agent to search the web for information"
            )
            st.session_state.tool_toggles["search_web"] = search_enabled

            if search_enabled:
                st.success("✅ Web search is enabled")
            else:
                st.warning("❌ Web search is disabled")

        with col2:
            st.subheader("📄 Document Retrieval")
            doc_enabled = st.checkbox(
                "Enable Document Retrieval Tool",
                value=st.session_state.tool_toggles["document_retrieval"],
                key="toggle_document_retrieval",
                help="Allow the agent to search through ingested documents"
            )
            st.session_state.tool_toggles["document_retrieval"] = doc_enabled

            if doc_enabled:
                st.success("✅ Document retrieval is enabled")
            else:
                st.warning("❌ Document retrieval is disabled")

        with col1:
            st.subheader("🗄️ SQL Query")
            sql_enabled = st.checkbox(
                "Enable SQL Query Tool",
                value=st.session_state.tool_toggles["sql_retrieval"],
                key="toggle_sql_retrieval",
                help="Allow the agent to query databases with SQL"
            )
            st.session_state.tool_toggles["sql_retrieval"] = sql_enabled

            if sql_enabled:
                st.success("✅ SQL query is enabled")
            else:
                st.warning("❌ SQL query is disabled")

        with col2:
            st.subheader("💻 Code Execution")
            code_enabled = st.checkbox(
                "Enable Code Execution Tool",
                value=st.session_state.tool_toggles["run_code"],
                key="toggle_run_code",
                help="Allow the agent to execute Python code"
            )
            st.session_state.tool_toggles["run_code"] = code_enabled

            if code_enabled:
                st.success("✅ Code execution is enabled")
            else:
                st.warning("❌ Code execution is disabled")

        enabled_tools_summary = get_enabled_tools()
        if enabled_tools_summary:
            st.subheader("✅ Currently Enabled Tools")
            st.caption("🔄 Tools will be used in this priority order: Documents → Databases → Web Search → Code")

            priority_order = {
                "document_retrieval": 1,
                "sql_retrieval": 2,
                "search_web": 3,
                "run_code": 4
            }

            sorted_tools = sorted(enabled_tools_summary, key=lambda x: priority_order.get(x["name"], 5))

            enabled_cols = st.columns(min(len(sorted_tools), 4))
            for i, tool in enumerate(sorted_tools):
                col_idx = i % 4
                priority_num = priority_order.get(tool["name"], 5)
                priority_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"][priority_num - 1] if priority_num <= 4 else "❓"
                with enabled_cols[col_idx]:
                    st.info(f"{priority_emoji} {tool['icon']} {tool['display_name']}")
        else:
            st.error("⚠️ No tools are currently enabled! The agent will not be able to perform any actions.")

elif current_page == "logs":
    st.title("🧾 Execution Logs")

    if not st.session_state.conversations:
        st.info("No conversations yet. Ask the agent a question to generate execution logs.")
    else:
        sorted_conversations = sorted(
            st.session_state.conversations.items(),
            key=lambda x: x[1].get("created_at", ""),
            reverse=True,
        )

        for idx, (conv_id, conv_data) in enumerate(sorted_conversations):
            conversation_title = get_conversation_title(conv_data, max_length=80)
            header = conversation_title
            with st.expander(header, expanded=(idx == 0)):
                created_at = conv_data.get("created_at", "Unknown")
                total_messages = len(conv_data.get("messages", []))
                total_tools_logged = len(conv_data.get("tools_used", []))
                st.caption(
                    f"Started {created_at} • Messages: {total_messages} • Tool calls logged: {total_tools_logged}"
                )

                conversation_logs = conv_data.get("execution_logs", [])

                if conversation_logs:
                    overview_tab, timeline_tab, raw_tab, tools_tab = st.tabs(
                        ["📊 Overview", "🔍 Detailed Timeline", "📝 Raw Logs", "🛠️ Tools Used"]
                    )

                    with overview_tab:
                        total_logs = len(conversation_logs)
                        log_types = {}
                        for log_entry in conversation_logs:
                            log_type = log_entry.get("type", "unknown")
                            log_types[log_type] = log_types.get(log_type, 0) + 1

                        cols = st.columns(min(len(log_types) + 1, 5))
                        with cols[0]:
                            st.metric("Total Log Entries", total_logs)

                        for i, (log_type, count) in enumerate(log_types.items()):
                            if i + 1 < len(cols):
                                with cols[i + 1]:
                                    emoji_map = {
                                        "execution_start": "🚀",
                                        "agent_execution": "🤖",
                                        "execution_overview": "📊",
                                        "error": "🚨",
                                        "query_timing": "⏱️",
                                    }
                                    emoji = emoji_map.get(log_type, "📝")
                                    st.metric(f"{emoji} {log_type.replace('_', ' ').title()}", count)

                        timing_entries = [
                            log_entry
                            for log_entry in conversation_logs
                            if log_entry.get("type") == "query_timing"
                        ]
                        if timing_entries:
                            duration_values = [
                                float(log_entry.get("duration_seconds", 0) or 0)
                                for log_entry in timing_entries
                            ]
                            total_queries = len(duration_values)
                            avg_duration = (
                                sum(duration_values) / total_queries if total_queries else 0.0
                            )
                            last_duration = duration_values[-1]
                            timing_cols = st.columns(3)
                            timing_cols[0].metric("Queries Logged", total_queries)
                            timing_cols[1].metric("Avg Query Time (s)", f"{avg_duration:.2f}")
                            timing_cols[2].metric("Last Query (s)", f"{last_duration:.2f}")

                        overview_logs = [
                            log_entry
                            for log_entry in conversation_logs
                            if log_entry.get("type") == "execution_overview"
                        ]
                        if overview_logs:
                            overview = overview_logs[-1]
                            st.subheader("📈 Execution Summary")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Steps", overview.get("total_steps", 0))
                            with col2:
                                st.metric("Total Messages", overview.get("total_messages", 0))
                            with col3:
                                st.metric("Tools Used", overview.get("tools_used_count", 0))

                            st.write("**Message Flow Timeline:**")
                            for msg_info in overview.get("message_flow", []):
                                col1, col2, col3, col4 = st.columns([1, 2, 3, 2])
                                with col1:
                                    st.write(f"#{msg_info['index']}")
                                with col2:
                                    st.write(f"**{msg_info['type']}**")
                                with col3:
                                    if msg_info["has_tool_calls"]:
                                        st.info(f"📞 {msg_info['tool_call_count']} tool call(s)")
                                    else:
                                        st.write(f"💬 {msg_info['content_length']} chars")
                                with col4:
                                    if msg_info.get("tool_call_ids"):
                                        st.code(f"IDs: {', '.join(msg_info['tool_call_ids'])}", language=None)

                    with timeline_tab:
                        st.subheader("⏱️ Execution Timeline")

                        timeline_logs = sorted(
                            conversation_logs, key=lambda x: x.get("timestamp", "")
                        )

                        for log_entry in timeline_logs:
                            log_type = log_entry.get("type", "unknown")
                            timestamp = log_entry.get("timestamp", "Unknown")

                            headers = {
                                "execution_start": "🚀 Execution Started",
                                "agent_execution": "🤖 Agent Processing",
                                "execution_overview": "📊 Execution Summary",
                                "error": "🚨 Execution Error",
                                "query_timing": "⏱️ Query Timing",
                            }

                            header = headers.get(log_type, f"📝 {log_type.replace('_', ' ').title()}")

                            with st.expander(f"{header}", expanded=False):
                                st.caption(f"🕒 {timestamp}")

                                if log_type == "execution_start":
                                    st.write("**Query Details:**")
                                    st.write(f"- **Query:** {log_entry.get('query', 'N/A')}")
                                    st.write(f"- **Available Tools:** {', '.join(log_entry.get('available_tools', []))}")

                                elif log_type == "agent_execution":
                                    st.write("**Agent Processing Details:**")
                                    st.write(f"- **Input Messages:** {log_entry.get('input_messages', 0)}")
                                    st.write(f"- **Result Type:** {log_entry.get('result_type', 'unknown')}")

                                elif log_type == "execution_overview":
                                    st.write("**Execution Statistics:**")
                                    st.write(f"- **Total Messages:** {log_entry.get('total_messages', 0)}")
                                    st.write(f"- **Step:** {log_entry.get('step', 0)}")

                                    st.write("**Message Flow:**")
                                    for msg in log_entry.get("message_flow", []):
                                        with st.container():
                                            st.write(f"**Message {msg['index']}: {msg['type']}**")
                                            st.write(f"Length: {msg['content_length']} chars")
                                            if msg["has_tool_calls"]:
                                                st.info(f"📞 {msg['tool_call_count']} tool call(s)")

                                elif log_type == "query_timing":
                                    duration = float(log_entry.get("duration_seconds", 0) or 0)
                                    st.write(f"**Query:** {log_entry.get('query', 'N/A')}")
                                    st.write(f"**Duration:** {duration:.2f} seconds")
                                    st.write(
                                        "**Tools Used:** "
                                        f"{', '.join(log_entry.get('tools_used', [])) or 'None'}"
                                    )
                                    st.write(f"**Started:** {log_entry.get('start_time', 'Unknown')}")
                                    st.write(f"**Finished:** {log_entry.get('end_time', 'Unknown')}")

                                elif log_type == "error":
                                    st.error("🚨 Execution Error")
                                    st.write(f"**Error:** {log_entry.get('error', 'Unknown error')}")
                                    st.write(f"**Step:** {log_entry.get('step', 'N/A')}")

                                else:
                                    st.json(log_entry)

                    with raw_tab:
                        st.subheader("🔧 Raw Execution Logs")
                        st.warning("⚠️ This view shows the complete raw log data for debugging purposes.")

                        for idx_log, log_entry in enumerate(conversation_logs, start=1):
                            log_type = log_entry.get("type", "unknown")
                            with st.expander(f"Raw Log {idx_log}: {log_type}", expanded=False):
                                st.json(log_entry)

                    with tools_tab:
                        tools_history = conv_data.get("tools_used", [])
                        if tools_history:
                            for idx_tool, tool in enumerate(tools_history, start=1):
                                if not isinstance(tool, dict):
                                    continue
                                status = tool.get("status", "unknown")
                                tool_header = f"{idx_tool}. {tool.get('tool_name', 'Tool')}"
                                if status:
                                    tool_header = f"{tool_header} • {str(status).title()}"
                                with st.expander(tool_header, expanded=False):
                                    st.write(f"**Call ID:** {tool.get('call_id', 'N/A')}")
                                    st.write(f"**Status:** {tool.get('status', 'unknown')}")
                                    if tool.get("timestamp"):
                                        st.write(f"**Timestamp:** {tool.get('timestamp')}")
                                    if tool.get("arguments"):
                                        st.write("**Arguments:**")
                                        st.json(tool.get("arguments"))
                                    if tool.get("response"):
                                        st.write("**Response:**")
                                        st.text_area(
                                            "Response",
                                            tool.get("response"),
                                            height=120,
                                            key=f"log_tool_response_{conv_id}_{idx_tool}",
                                        )
                        else:
                            st.info("No tools have been recorded for this conversation yet.")

                else:
                    st.info("No execution logs available yet for this conversation.")

# Footer
st.divider()
st.caption("Built with LangGraph, LangChain, and Streamlit • Powered by GPT-4o-mini")
