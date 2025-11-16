import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
import os
import subprocess
from pathlib import Path
from tools.config import update_enabled_documents, update_enabled_databases

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
            button_label = f"{conv_id.replace('conv_', 'Conversation ')}"
            created_time = conv_data["created_at"]

            # Show preview of first message if available
            preview = ""
            if conv_data["messages"]:
                first_msg = conv_data["messages"][0]
                if hasattr(first_msg, 'content'):
                    preview = first_msg.content[:50] + "..." if len(first_msg.content) > 50 else first_msg.content

            # Use columns for better layout
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"{button_label}\n{created_time}", key=f"conv_{conv_id}"):
                    st.session_state.current_conversation_id = conv_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{conv_id}", help="Delete conversation"):
                    del st.session_state.conversations[conv_id]
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

        with st.spinner("🤖 Agent is thinking..."):
            try:
                enabled_tool_functions = get_enabled_tool_functions()

                if not enabled_tool_functions:
                    error_msg = "No tools are enabled. Please enable at least one tool in the Tool Management section."
                    ai_message = AIMessage(content=error_msg)
                    current_conv["messages"].append(ai_message)
                    update_current_conversation(messages=current_conv["messages"])
                    tools_used = []
                    execution_logs = [{"type": "error", "message": "No tools enabled"}]
                else:
                    from langgraph_main import create_agent_with_tools, run_agent_query_with_tools

                    agent = create_agent_with_tools(enabled_tool_functions)
                    response, tools_used, execution_logs = run_agent_query_with_tools(agent, prompt)

                    ai_message = AIMessage(content=response)
                    current_conv["messages"].append(ai_message)
                    update_current_conversation(
                        messages=current_conv["messages"],
                        tools_used=tools_used,
                        execution_logs=execution_logs
                    )

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                ai_message = AIMessage(content=error_msg)
                current_conv["messages"].append(ai_message)
                update_current_conversation(messages=current_conv["messages"])
                tools_used = []
                execution_logs = [{"type": "error", "message": str(e)}]

        assistant_reply = ai_message.content

        with chat_container:
            with st.chat_message("assistant"):
                st.write(assistant_reply)

        st.rerun()

elif current_page == "settings":
    st.title("⚙️ Settings & Tools")
    st.subheader("🔧 Tools Used")

    if current_conv["tools_used"]:
        cols = st.columns(min(len(current_conv["tools_used"]), 3))

        for i, tool in enumerate(current_conv["tools_used"]):
            col_idx = i % 3
            with cols[col_idx]:
                with st.container():
                    if tool["status"] == "completed":
                        st.success(f"✅ {tool['tool_name']}")
                    elif tool["status"] == "called":
                        st.warning(f"⏳ {tool['tool_name']}")
                    else:
                        st.error(f"❌ {tool['tool_name']}")

                    with st.expander(f"Details for {tool['tool_name']}", expanded=False):
                        st.write(f"**Call ID:** {tool['call_id']}")
                        st.write(f"**Status:** {tool['status']}")

                        if tool.get("arguments"):
                            st.write("**Arguments:**")
                            st.json(tool["arguments"])

                        if tool.get("response"):
                            st.write("**Response:**")
                            st.text_area(
                                "Response",
                                tool["response"],
                                height=100,
                                key=f"response_{tool['call_id']}"
                            )

                        if tool.get("timestamp"):
                            st.write(f"**Timestamp:** {tool['timestamp']}")
    else:
        st.info("No tools were used in this conversation yet.")

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

    if current_conv["execution_logs"]:
        log_tab1, log_tab2, log_tab3 = st.tabs(["📊 Overview", "🔍 Detailed Timeline", "📝 Raw Logs"])

        with log_tab1:
            total_logs = len(current_conv["execution_logs"])

            log_types = {}
            for log in current_conv["execution_logs"]:
                log_type = log.get("type", "unknown")
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
                            "error": "🚨"
                        }
                        emoji = emoji_map.get(log_type, "📝")
                        st.metric(f"{emoji} {log_type.replace('_', ' ').title()}", count)

            overview_logs = [log for log in current_conv["execution_logs"] if log.get("type") == "execution_overview"]
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

        with log_tab2:
            st.subheader("⏱️ Execution Timeline")

            timeline_logs = sorted(current_conv["execution_logs"], key=lambda x: x.get("timestamp", ""))

            for log_entry in timeline_logs:
                log_type = log_entry.get("type", "unknown")
                timestamp = log_entry.get("timestamp", "Unknown")

                headers = {
                    "execution_start": "🚀 Execution Started",
                    "agent_execution": "🤖 Agent Processing",
                    "execution_overview": "📊 Execution Summary",
                    "error": "🚨 Execution Error"
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

                    elif log_type == "error":
                        st.error("🚨 Execution Error")
                        st.write(f"**Error:** {log_entry.get('error', 'Unknown error')}")
                        st.write(f"**Step:** {log_entry.get('step', 'N/A')}")

                    else:
                        st.json(log_entry)

        with log_tab3:
            st.subheader("🔧 Raw Execution Logs")
            st.warning("⚠️ This view shows the complete raw log data for debugging purposes.")

            for i, log_entry in enumerate(current_conv["execution_logs"]):
                log_type = log_entry.get("type", "unknown")
                with st.expander(f"Raw Log {i+1}: {log_type}", expanded=False):
                    st.json(log_entry)

    else:
        st.info("No execution logs available yet. Ask the agent a question to see the execution details.")

# Footer
st.divider()
st.caption("Built with LangGraph, LangChain, and Streamlit • Powered by GPT-4o-mini")
