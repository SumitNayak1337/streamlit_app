import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from template import REPORT_TEMPLATES
from document import create_docx_from_text

st.set_page_config(page_title="NEXUS AI", layout="wide")

# Initialize API
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
MODEL_ID = "models/gemini-3.1-pro-preview"

# Load Custom Knowledge Base (Portfolio & Checklists)
def load_knowledge_base():
    try:
        with open("nexus_knowledge.txt", "r", encoding="utf-8") as file:
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
if "latest_report_docx" not in st.session_state:
    st.session_state.latest_report_docx = None
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

st.title("🛡️ NEXUS - Custom CyberSec Agent")

with st.sidebar:
    st.subheader("Report Configuration")
    selected_template = st.selectbox("Select Report Template", ["None"] + list(REPORT_TEMPLATES.keys()))
    
    st.subheader("Analysis Evidence")
    # Enabled multiple file uploads
    uploaded_files = st.file_uploader("Upload logs or screenshots", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key=f"uploader_{st.session_state.uploader_key}")
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} files staged for analysis.")
        for file in uploaded_files:
            st.image(file, caption=file.name, use_container_width=True)
            
    if st.button("Clear Session"):
        st.session_state.chat_session = init_model().start_chat(history=[])
        st.session_state.latest_report_docx = None
        st.session_state.uploader_key += 1
        st.rerun()
        
    if st.session_state.latest_report_docx is not None:
        st.divider()
        st.subheader("Generated Output")
        st.download_button(
            label="📄 Download Report as DOCX",
            data=st.session_state.latest_report_docx,
            file_name="nexus_security_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

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
    augmented_input = user_input
    if selected_template != "None":
        augmented_input += "\n\n### SYSTEM INSTRUCTION OVERRIDE / TEMPLATE ###\n" + REPORT_TEMPLATES[selected_template]

    payload = []
    images_dict = {}
    if uploaded_files:
        image_names = []
        for file in uploaded_files:
            file.seek(0)
            images_dict[file.name] = file
            payload.append(Image.open(file))
            image_names.append(file.name)
            
        augmented_input += "\n\nAttached Evidence Files:\n" + "\n".join(f"- {name}" for name in image_names)
        augmented_input += "\n\nIMPORTANT INSTRUCTION: If you want to embed a screenshot exactly where it fits in the report, use this exact formatting on its own line: `[IMAGE: filename.ext]` replacing filename.ext with the exact name from the list above. Our parser will replace that text with the actual image."

    # Append the text prompt at the END of the images for better analysis
    payload.append(augmented_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing against custom checklists..."):
            try:
                response = st.session_state.chat_session.send_message(payload)
                st.markdown(response.text)
                
                # Generate DOCX and save it to session state
                docx_file = create_docx_from_text(response.text, images_dict)
                st.session_state.latest_report_docx = docx_file
                
                # Force a rerun to show the download button in the sidebar instantly
                st.rerun()
            except Exception as e:
                st.error(f"Execution Error: {e}")