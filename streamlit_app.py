import streamlit as st
import requests

st.set_page_config(page_title="Drive File Assistant", page_icon="📁")
st.title("📁 Google Drive File Assistant")
st.caption("Ask me to find any file in your Drive")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Search for files..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                response = requests.post(
                    "http://localhost:8001/chat",
                    json={"message": prompt}
                )
                answer = response.json()["response"]
            except Exception as e:
                answer = f"Error connecting to backend: {str(e)}"
        st.write(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})