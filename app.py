import os
import time
import json
import uuid
import traceback
import streamlit as st
from customer_support import app as agent_graph

HISTORY_FILE = "chat_history.json"

st.set_page_config(page_title="Help Center", page_icon="💬", layout="centered")

st.markdown("""
    <style>
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stChatInputContainer {padding-bottom: 20px;}
        .support-header {
            background-color: #111111;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 25px;
            border: 1px solid #222222;
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

def load_local_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_local_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

all_history = load_local_history()

with st.sidebar:
    st.title("📂 Chat History")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
        
    st.markdown("---")
    
    if all_history:
        st.caption("Past Conversations:")
        for saved_thread_id, messages in list(all_history.items()):
            first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), "Empty Chat")
            truncated_title = first_user_msg[:24] + "..." if len(first_user_msg) > 24 else first_user_msg
            
            if st.button(f"💬 {truncated_title}", key=f"sidebar_{saved_thread_id}", use_container_width=True):
                st.session_state.thread_id = saved_thread_id
                st.rerun()
    else:
        st.caption("No past sessions found.")

if "thread_id" not in st.session_state:
    if all_history:
        st.session_state.thread_id = list(all_history.keys())[0]
    else:
        st.session_state.thread_id = str(uuid.uuid4())

if st.session_state.thread_id in all_history:
    st.session_state.messages = all_history[st.session_state.thread_id]
else:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hello! I am your dedicated support assistant. How can I help you with your order or policy inquiries today?", 
            "agent": "Support Concierge"
        }
    ]

# Main Canvas Header updated to Customer Support Agent
st.markdown("""
    <div class="support-header">
        <h2 style='margin:0; padding-bottom:6px; color:#ffffff;'>💬 Customer Support Agent</h2>
        <p style='margin:0; color:#b3b3b3; font-size:14px;'>Ask us about shipping updates, order tracking, or return policies.</p>
    </div>
""", unsafe_allow_html=True)

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.caption(f"🤖 {msg.get('agent', 'Support Agent')}")
        st.write(msg["content"])
        
        if msg["role"] == "assistant" and i > 0:
            feedback_key = f"feedback_{st.session_state.thread_id}_{i}"
            col1, col2, _ = st.columns([0.05, 0.05, 0.9])
            current_feedback = msg.get("feedback", None)
            
            with col1:
                if st.button("👍", key=f"up_{feedback_key}", help="Helpful"):
                    msg["feedback"] = "thumbs_up"
                    all_history[st.session_state.thread_id] = st.session_state.messages
                    save_local_history(all_history)
                    st.toast("Thank you for your feedback!", icon="✨")
            with col2:
                if st.button("👎", key=f"down_{feedback_key}", help="Not Helpful"):
                    msg["feedback"] = "thumbs_down"
                    all_history[st.session_state.thread_id] = st.session_state.messages
                    save_local_history(all_history)
                    st.toast("Feedback recorded. We'll improve!", icon="📝")
            
            if current_feedback:
                st.caption(f"*You rated this:* `{'Helpful' if current_feedback == 'thumbs_up' else 'Not Helpful'}`")

if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    all_history[st.session_state.thread_id] = st.session_state.messages
    save_local_history(all_history)
    st.rerun()

if st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        with st.spinner("Connecting with a specialist..."):
            try:
                initial_state = {
                    "customer_query": user_query,
                    "agent_logs": [],
                    "current_agent": "",
                    "resolution": "",
                    "order_id": None
                }
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                
                final_state = agent_graph.invoke(initial_state, config=config)
                
                reply = final_state.get("resolution", "I apologize, I am unable to process your request at this time.")
                agent_type = final_state.get("current_agent", "Support").title() + " Specialist"
                
                st.caption(f"🤖 {agent_type}")
                
                placeholder = st.empty()
                full_response = ""
                for word in reply.split(" "):
                    full_response += word + " "
                    placeholder.markdown(full_response + "▌")
                    time.sleep(0.04)
                placeholder.markdown(full_response)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": reply, 
                    "agent": agent_type,
                    "feedback": None
                })
                
                all_history[st.session_state.thread_id] = st.session_state.messages
                save_local_history(all_history)
                st.rerun()
                
            except Exception as e:
                st.error("An internal execution error occurred. Here is the traceback:")
                st.code(traceback.format_exc(), language="python")
