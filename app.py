import streamlit as st
import requests
import time
import os

# UI Configuration
st.set_page_config(page_title="Avvaiyar Paatti 👵", page_icon="🌿", layout="centered")

# CSS for the chat interface
st.markdown("""
<style>
    .stChatMessage { border-radius: 20px; padding: 15px; font-family: 'Georgia', serif; font-size: 16px; }
    .bot-message { background-color: #fffde7; border: 1px solid #e6e6e6; }
    .stButton button { background-color: #2E7D32; color: white; border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

# 1. Get the Brain URL
API_URL = st.secrets.get("API_URL", "https://gsr-608001-avvaiyar-brain.hf.space/chat")

# Sidebar Status
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Avvaiyar_Statue_Marina_Beach_Chennai.jpg")
    st.markdown("### 🌿 Brain Status")
    
    # Check if we have a latency recorded in session state
    if "last_latency" in st.session_state:
        latency = st.session_state.last_latency
        if latency > 10:
            st.warning(f"🐢 Waking up: {latency:.1f}s")
            st.caption("Paatti was sleeping. She is awake now!")
        else:
            st.success(f"⚡ Active: {latency:.1f}s")
            st.caption("Paatti is awake and fast.")
    else:
        st.info("💤 Status: Unknown (Waiting for first message)")

st.title("👵 Avvaiyar Paatti's Advice")
st.markdown("*\"Om Namah Shivaya... Come, tell Paatti what is on your mind.\"*")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Logic
if user_input := st.chat_input("Type here... (e.g., I am feeling sad)"):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Start the Timer
        start_time = time.time()
        
        # Dynamic Loading Message
        with st.spinner("👵 Paatti is listening... (If she is sleeping, this might take a minute to wake her up!)"):
            try:
                # High timeout to allow the "Wake Up" phase
                response = requests.post(API_URL, json={"query": user_input}, timeout=600)
                
                # Stop the Timer
                end_time = time.time()
                duration = end_time - start_time
                st.session_state.last_latency = duration # Save for sidebar

                if response.status_code == 200:
                    bot_text = response.json()["response"]
                    
                    # Logic: If it took long, acknowledge it!
                    if duration > 10:
                        prefix = f"*(Paatti just woke up! That took {int(duration)} seconds. Next time I'll be faster!)* \n\n"
                        bot_text = prefix + bot_text
                    
                    # Typewriter Effect
                    full_response = ""
                    for chunk in bot_text.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                else:
                    st.error(f"❌ Paatti is confused (Error {response.status_code})")
                    st.write(response.text)
            
            except Exception as e:
                st.error("🚨 Connection Issue")
                st.write(f"Error details: {e}")
