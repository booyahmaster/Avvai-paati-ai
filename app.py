import streamlit as st
import requests
import time
import os

st.set_page_config(page_title="Avvaiyar Paatti 👵", page_icon="🌿", layout="centered")

st.markdown("""
<style>
    .stChatMessage { border-radius: 20px; padding: 15px; font-family: 'Georgia', serif; font-size: 16px; }
    .bot-message { background-color: #fffde7; border: 1px solid #e6e6e6; }
    .stButton button { background-color: #2E7D32; color: white; border-radius: 20px; }
    h1 { color: #1B5E20; font-family: 'Helvetica', sans-serif; }
</style>
""", unsafe_allow_html=True)

# Cloud-ready URL check
API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Avvaiyar_Statue_Marina_Beach_Chennai.jpg")
    st.markdown("### 🌿 Daily Wisdom")
    st.caption("Powered by Siva's Fine-Tuned Model")

st.title("👵 Avvaiyar Paatti's Advice")
st.markdown("*\"Come, sit by me my child. Tell Paatti what is heavy on your heart...\"*")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Talk to Paatti..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Paatti is listening... 🌿"):
            try:
                response = requests.post(API_URL, json={"query": user_input})
                if response.status_code == 200:
                    bot_text = response.json()["response"]
                    
                    # Streaming effect for "Gentle" feeling
                    full_response = ""
                    for chunk in bot_text.split():
                        full_response += chunk + " "
                        time.sleep(0.05) 
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.error("👵 Paatti is resting. (Check if api.py is running)")
            except:
                st.error("🚨 Connection Error: Start the Brain (api.py) first!")