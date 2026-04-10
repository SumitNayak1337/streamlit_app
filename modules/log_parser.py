import streamlit as st
import pandas as pd
import json

def render_log_parser():
    st.header("📄 Advanced Log Parsing")
    st.write("Upload raw logs to parse, filter, and extract IOCs.")
    
    log_type = st.selectbox("Select Log Format", ["CSV", "JSON / JSONL", "Apache/Nginx", "Syslog", "Nmap XML"])
    uploaded_file = st.file_uploader(f"Upload {log_type} file", type=["csv", "json", "jsonl", "log", "txt", "xml"])
    
    if uploaded_file is not None:
        try:
            if log_type == "CSV":
                df = pd.read_csv(uploaded_file)
                st.write(f"Loaded {len(df)} rows.")
                st.dataframe(df)
            elif log_type in ["JSON / JSONL"]:
                if uploaded_file.name.endswith(".jsonl"):
                    df = pd.read_json(uploaded_file, lines=True)
                else:
                    df = pd.read_json(uploaded_file)
                st.dataframe(df)
            else:
                st.info(f"Custom parser for {log_type} is still in development.")
                # Show first few lines
                content = uploaded_file.getvalue().decode("utf-8").split("\n")[:10]
                st.text("Preview:\n" + "\n".join(content))
        except Exception as e:
            st.error(f"Error parsing log file: {e}")
