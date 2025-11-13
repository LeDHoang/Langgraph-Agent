import streamlit as st
from datetime import datetime
from langgraph_main import run_agent_query
from langchain_core.messages import HumanMessage, AIMessage

# Page configuration
st.set_page_config(
    page_title="LangGraph Agent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "conversation_counter" not in st.session_state:
    st.session_state.conversation_counter = 1

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

# Main content area
st.title("🤖 LangGraph Agent Chat")

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

# Display chat messages
st.subheader("Chat")

# Create a container for messages
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
            # Handle other message types
            with st.chat_message("system"):
                st.write(f"System: {message.content}")

# Chat input
if prompt := st.chat_input("Ask the LangGraph agent anything..."):
    # Add user message to conversation
    user_message = HumanMessage(content=prompt)
    current_conv["messages"].append(user_message)

    # Update the conversation in session state
    update_current_conversation(messages=current_conv["messages"])

    # Show user message immediately
    with chat_container:
        with st.chat_message("user"):
            st.write(prompt)

    # Show loading spinner while processing
    with st.spinner("🤖 Agent is thinking..."):
        try:
            # Call the agent
            response, tools_used, execution_logs = run_agent_query(prompt)

            # Create AI message
            ai_message = AIMessage(content=response)
            current_conv["messages"].append(ai_message)

            # Update conversation with results
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

    # Show AI response
    with chat_container:
        with st.chat_message("assistant"):
            st.write(response)

    # Force a rerun to update the UI
    st.rerun()

# Tool Usage Display
st.subheader("🔧 Tools Used")

if current_conv["tools_used"]:
    # Create columns for tool display
    cols = st.columns(min(len(current_conv["tools_used"]), 3))

    for i, tool in enumerate(current_conv["tools_used"]):
        col_idx = i % 3
        with cols[col_idx]:
            with st.container():
                # Tool status indicator
                if tool["status"] == "completed":
                    st.success(f"✅ {tool['tool_name']}")
                elif tool["status"] == "called":
                    st.warning(f"⏳ {tool['tool_name']}")
                else:
                    st.error(f"❌ {tool['tool_name']}")

                # Tool details in expander
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

# Execution Logs Display
st.subheader("📋 Execution Logs")

if current_conv["execution_logs"]:
    # Use tabs for different log views
    log_tab1, log_tab2 = st.tabs(["📊 Summary", "🔍 Detailed Logs"])

    with log_tab1:
        # Summary view
        total_logs = len(current_conv["execution_logs"])
        state_snapshots = sum(1 for log in current_conv["execution_logs"] if log.get("type") == "state_snapshot")
        debug_traces = sum(1 for log in current_conv["execution_logs"] if log.get("type") == "debug_trace")
        errors = sum(1 for log in current_conv["execution_logs"] if log.get("type") == "error")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Log Entries", total_logs)
        with col2:
            st.metric("State Snapshots", state_snapshots)
        with col3:
            st.metric("Debug Traces", debug_traces)
        with col4:
            st.metric("Errors", errors)

        # Show execution overview if available
        overview_logs = [log for log in current_conv["execution_logs"] if log.get("type") == "execution_overview"]
        if overview_logs:
            overview = overview_logs[0]
            st.write("**Message Flow:**")
            for msg_info in overview.get("message_flow", []):
                if msg_info["has_tool_calls"]:
                    st.info(f"Message {msg_info['index']}: {msg_info['type']} with {msg_info['tool_call_count']} tool calls")
                else:
                    st.write(f"Message {msg_info['index']}: {msg_info['type']} ({msg_info['content_length']} chars)")

    with log_tab2:
        # Detailed logs view
        for i, log_entry in enumerate(current_conv["execution_logs"]):
            log_type = log_entry.get("type", "unknown")

            if log_type == "execution_overview":
                with st.expander(f"📊 Execution Overview (Step {i+1})", expanded=False):
                    st.json(log_entry)

            elif log_type == "state_snapshot":
                with st.expander(f"🔄 State Snapshot (Step {i+1})", expanded=False):
                    st.write(f"**Messages:** {log_entry.get('messages_count', 0)}")
                    st.write(f"**Node:** {log_entry.get('current_node', 'unknown')}")
                    if log_entry.get("messages"):
                        st.write("**Recent Messages:**")
                        for msg in log_entry["messages"]:
                            if msg["has_tool_calls"]:
                                st.info(f"• {msg['type']}: {msg['content_preview']} (has tool calls)")
                            else:
                                st.write(f"• {msg['type']}: {msg['content_preview']}")

            elif log_type == "debug_trace":
                with st.expander(f"🐛 Debug Trace (Step {i+1})", expanded=False):
                    st.write(f"**Node:** {log_entry.get('node_name', 'unknown')}")
                    st.write(f"**Operation:** {log_entry.get('operation', 'unknown')}")
                    if log_entry.get("debug_summary"):
                        st.code(log_entry["debug_summary"], language="text")

            elif log_type == "error":
                with st.expander(f"❌ Error (Step {i+1})", expanded=True):
                    st.error(f"**Error:** {log_entry.get('error', 'Unknown error')}")
                    if log_entry.get("message"):
                        st.write(f"**Details:** {log_entry['message']}")

            else:
                with st.expander(f"📝 Log Entry {i+1} ({log_type})", expanded=False):
                    st.json(log_entry)
else:
    st.info("No execution logs available yet. Ask the agent a question to see the execution details.")

# Footer
st.divider()
st.caption("Built with LangGraph, LangChain, and Streamlit • Powered by GPT-4o-mini")
