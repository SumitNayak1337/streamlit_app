import streamlit as st
import requests

def render_threat_intel():
    st.header("🔍 Threat Intelligence")
    st.write("Lookup real-time threat intelligence data.")
    
    tab1, tab2, tab3 = st.tabs(["CVE Lookup", "IP Reputation", "Hash Analysis"])
    
    with tab1:
        st.subheader("NVD CVE Lookup")
        cve_id = st.text_input("Enter CVE ID (e.g., CVE-2021-44228)")
        if st.button("Search CVE"):
            if cve_id:
                with st.spinner("Querying NVD Database..."):
                    try:
                        resp = requests.get(f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}")
                        if resp.status_code == 200:
                            data = resp.json()
                            if data.get("totalResults", 0) > 0:
                                vuln = data["vulnerabilities"][0]["cve"]
                                st.success(f"Found {cve_id}")
                                st.markdown(f"**Description:** {vuln['descriptions'][0]['value']}")
                                st.json(vuln)
                            else:
                                st.warning("CVE not found.")
                        else:
                            st.error(f"API Error: {resp.status_code}")
                    except Exception as e:
                        st.error(f"Failed to fetch data: {e}")
            else:
                st.warning("Please enter a CVE ID")

    with tab2:
        st.subheader("IP Reputation Checker")
        ip = st.text_input("Enter IP Address")
        if st.button("Check IP"):
            st.info("AbuseIPDB integration placeholder - requires API Key.")
            # Placeholder for AbuseIPDB integration

    with tab3:
        st.subheader("Hash Analysis")
        file_hash = st.text_input("Enter File Hash (MD5, SHA1, SHA256)")
        if st.button("Check Hash"):
            st.info("VirusTotal integration placeholder - requires API Key.")
