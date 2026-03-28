import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

st.set_page_config(page_title="NEXUS AI", layout="wide")

# Initialize API
api_key = st.secrets["GEMINI_API_KEY"] 
genai.configure(api_key=api_key)
MODEL_ID = "models/gemini-3.1-pro-preview"

# Load Custom Knowledge Base (Portfolio & Checklists)
def load_knowledge_base():
    try:
        with open("nexus_knowledge.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "Knowledge base file not found. Running with default context."

# Dynamic System Prompt
SYSTEM_PROMPT = f"""You are NEXUS, an elite cybersecurity AI assistant developed by Sumit Nayak.
You must strictly follow Sumit's predefined checklists for any analysis.

Below is Sumit's Portfolio and Custom Knowledge Base:
{load_knowledge_base()}

Your rules:
1. When asked about Sumit, use the provided portfolio data.
2. When analyzing vulnerabilities or logs, cross-reference and suggest steps from Sumit's Checklists.
3. Be highly technical, direct, and implementation-focused. Zero fluff."""

@st.cache_resource
def init_model():
    return genai.GenerativeModel(
        model_name=MODEL_ID,
        system_instruction=SYSTEM_PROMPT
    )

if "chat_session" not in st.session_state:
    st.session_state.chat_session = init_model().start_chat(history=[])

st.title("🛡️ NEXUS - Custom CyberSec Agent")

with st.sidebar:
    st.subheader("Analysis Evidence")
    # Enabled multiple file uploads
    uploaded_files = st.file_uploader("Upload logs or screenshots", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} files staged for analysis.")
        for file in uploaded_files:
            st.image(file, caption=file.name, use_container_width=True)
            
    if st.button("Clear Session"):
        st.session_state.chat_session = init_model().start_chat(history=[])
        st.rerun()

# Display Chat History
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        for part in message.parts:
            if hasattr(part, 'text') and part.text:
                st.markdown(part.text)

user_input = st.chat_input("Ask NEXUS, paste logs, or reference a checklist...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build the payload with text and ALL uploaded images
    payload = [user_input]
    if uploaded_files:
        for file in uploaded_files:
            payload.append(Image.open(file))

    with st.chat_message("assistant"):
        with st.spinner("Analyzing against custom checklists..."):
            try:
                response = st.session_state.chat_session.send_message(payload)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Execution Error: {e}")