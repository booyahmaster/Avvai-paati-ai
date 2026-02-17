import streamlit as st
import requests
import time

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Avvaiyar Paatti AI",
    page_icon="👵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Tamil-friendly font */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,700;1,400&display=swap');

    .main { background-color: #FDF6EC; }

    /* Header */
    .paatti-header {
        text-align: center;
        padding: 1.2rem 0 0.5rem 0;
    }
    .paatti-header h1 {
        font-family: 'Noto Serif', serif;
        color: #7A3B00;
        font-size: 2.2rem;
        margin-bottom: 0.1rem;
    }
    .paatti-header .tamil {
        font-size: 1.1rem;
        color: #C47A2B;
        font-style: italic;
    }
    .paatti-header .tagline {
        font-size: 0.9rem;
        color: #8B6343;
        margin-top: 0.3rem;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 0.4rem;
    }

    /* User bubble */
    [data-testid="stChatMessageContent"] {
        font-size: 1rem;
    }

    /* Verse highlight inside response */
    .verse-box {
        background: #FFF3DC;
        border-left: 4px solid #E07B00;
        padding: 0.5rem 0.8rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        font-style: italic;
        color: #5C3100;
    }

    /* Input box */
    .stChatInput textarea {
        border-radius: 20px !important;
        border-color: #E07B00 !important;
    }

    /* Sidebar */
    .example-btn {
        background: #FFF3DC;
        border: 1px solid #E07B00;
        border-radius: 8px;
        padding: 0.4rem 0.7rem;
        color: #7A3B00;
        cursor: pointer;
        width: 100%;
        text-align: left;
        margin-bottom: 0.4rem;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────
# Replace YOUR_HF_USERNAME with your actual Hugging Face username
# This points to your HF Space running the FastAPI backend
API_URL = st.secrets.get("API_URL", "https://GSR-608001-avvaiyar-paatti-api.hf.space/chat")

# ── Header ────────────────────────────────────────────────────────
st.markdown("""
<div class="paatti-header">
    <h1>👵 Avvaiyar Paatti AI</h1>
    <div class="tamil">ஔவையார் பாட்டி</div>
    <div class="tagline">Ancient Tamil wisdom for modern life — ask me anything</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Sidebar with example questions ───────────────────────────────
with st.sidebar:
    st.markdown("### 💬 Try asking Paatti...")
    examples = [
        "I keep procrastinating my work",
        "My friend betrayed my trust",
        "I am losing motivation to study",
        "How do I deal with an arrogant person?",
        "I want to be successful but don't know where to start",
        "I feel lazy and don't want to do anything",
        "Someone spoke badly about me behind my back",
        "I am angry and can't control it",
    ]
    for ex in examples:
        if st.button(ex, key=ex, use_container_width=True):
            st.session_state["prefill"] = ex

    st.divider()
    st.caption("Powered by Gemini 2.0 Flash + RAG\nData: Aathichoodi by Avvaiyar")

# ── Chat history ──────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Greeting on first load
    st.session_state.messages.append({
        "role": "assistant",
        "content": "வணக்கம் Kanna! 🙏\n\nI am Avvaiyar Paatti. Come to me with whatever is weighing on your heart — work, relationships, self-doubt, anything. I will share what the ancient Aathichoodi teaches us.\n\nWhat is on your mind today?"
    })

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👵" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])

# ── Handle sidebar prefill ────────────────────────────────────────
prefill = st.session_state.pop("prefill", None)

# ── Chat input ────────────────────────────────────────────────────
user_input = st.chat_input("Tell Paatti what's on your mind...") or prefill

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Get response from backend
    with st.chat_message("assistant", avatar="👵"):
        placeholder = st.empty()

        with st.spinner("Paatti is thinking... 🤔"):
            try:
                resp = requests.post(
                    API_URL,
                    json={"query": user_input},
                    timeout=25,
                )

                if resp.status_code == 200:
                    bot_text = resp.json().get("response", "")

                    # Stream word by word for a natural feel
                    displayed = ""
                    for word in bot_text.split():
                        displayed += word + " "
                        placeholder.markdown(displayed + "▌")
                        time.sleep(0.035)
                    placeholder.markdown(displayed.strip())

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": displayed.strip(),
                    })

                elif resp.status_code == 503:
                    placeholder.warning("Paatti is waking up — please send your message again in a few seconds 🙏")

                else:
                    placeholder.error(f"Something went wrong (error {resp.status_code}). Please try again.")

            except requests.exceptions.Timeout:
                placeholder.error("The response took too long. Please try again — Paatti is still here 🙏")
            except requests.exceptions.ConnectionError:
                placeholder.error("Cannot reach the backend. Please check if the HF Space is running.")
            except Exception as e:
                placeholder.error(f"Unexpected error: {str(e)}")
