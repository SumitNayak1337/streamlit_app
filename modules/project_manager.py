import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "nexus_projects.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY, name TEXT, date TEXT, description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS findings
                 (id INTEGER PRIMARY KEY, project_id INTEGER, title TEXT, severity TEXT, status TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def render_project_manager():
    st.header("💾 Project & Findings Manager")
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    
    tab_projects, tab_findings = st.tabs(["Projects", "Findings Tracker"])
    
    with tab_projects:
        st.subheader("Manage Projects")
        with st.form("new_project"):
            p_name = st.text_input("Project Name")
            p_desc = st.text_area("Description")
            if st.form_submit_button("Create Project"):
                if p_name:
                    c = conn.cursor()
                    c.execute("INSERT INTO projects (name, date, description) VALUES (?, ?, ?)", 
                              (p_name, datetime.now().strftime("%Y-%m-%d %H:%M"), p_desc))
                    conn.commit()
                    st.success(f"Project '{p_name}' created!")
                else:
                    st.error("Project name required.")
                    
        st.markdown("### Existing Projects")
        df_proj = pd.read_sql_query("SELECT * FROM projects", conn)
        st.dataframe(df_proj, hide_index=True)

    with tab_findings:
        st.subheader("Add Finding")
        projects = pd.read_sql_query("SELECT id, name FROM projects", conn)
        
        if projects.empty:
            st.warning("Create a project first to add findings.")
        else:
            with st.form("new_finding"):
                proj_dict = dict(zip(projects.name, projects.id))
                selected_proj = st.selectbox("Project", projects.name.tolist())
                f_title = st.text_input("Finding Title")
                f_sev = st.selectbox("Severity", ["Critical", "High", "Medium", "Low", "Info"])
                
                if st.form_submit_button("Save Finding"):
                    if f_title:
                        c = conn.cursor()
                        c.execute("INSERT INTO findings (project_id, title, severity, status, date) VALUES (?, ?, ?, ?, ?)",
                                  (proj_dict[selected_proj], f_title, f_sev, "Open", datetime.now().strftime("%Y-%m-%d %H:%M")))
                        conn.commit()
                        st.success("Finding saved!")
                    else:
                        st.error("Title is required.")
                        
            st.markdown("### All Findings")
            df_find = pd.read_sql_query('''
                SELECT f.id, p.name as Project, f.title as Finding, f.severity as Severity, f.status as Status, f.date as Logged
                FROM findings f 
                JOIN projects p ON f.project_id = p.id
            ''', conn)
            st.dataframe(df_find, hide_index=True)
            
    conn.close()
