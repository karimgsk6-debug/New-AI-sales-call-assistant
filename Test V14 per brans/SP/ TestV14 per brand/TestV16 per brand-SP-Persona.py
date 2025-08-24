import streamlit as st
from groq import Groq
import os

# --- Page Config ---
st.set_page_config(page_title="AI Sales Call Assistant", layout="wide")

# --- Initialize Groq client ---
groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", "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"))
if not groq_api_key:
    st.warning("⚠️ No Groq API key found. Please add it in Streamlit secrets or as an environment variable.")
client = Groq(api_key=groq_api_key) if groq_api_key else None

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "reset" not in st.session_state:
    st.session_state.reset = False

# --- Title ---
st.title("🧠 AI Sales Call Assistant")
st.markdown("Prepare for HCP visits with AI-powered suggestions tailored to persona, behaviors, and barriers.")

# --- Reset selections ---
if st.button("🔄 Reset Selections"):
    st.session_state.reset = True
    st.session_state.chat_history = []

# --- Filters ---
col1, col2, col3 = st.columns(3)

with col1:
    brand = st.selectbox(
        "Select Brand",
        ["Brand A", "Brand B", "Brand C"],
        index=0 if not st.session_state.reset else 0
    )

with col2:
    behaviors = st.multiselect(
        "Select HCP Behaviors",
        ["Scientific", "Skeptical", "Time-Pressured", "Collaborative"],
        default=[] if st.session_state.reset else None
    )

with col3:
    barriers = st.multiselect(
        "Select HCP Barriers",
        ["Lack of Awareness", "Cost Concerns", "Efficacy Doubts", "Safety Concerns"],
        default=[] if st.session_state.reset else None
    )

# --- Persona filter ---
persona = st.multiselect(
    "Select HCP Persona",
    ["Friendly", "Masked", "Senior", "Junior", "Scientific", "Emotional"],
    default=[] if st.session_state.reset else None
)

# --- Tone Options ---
col4, col5 = st.columns(2)
with col4:
    response_length = st.radio("Response Length", ["Short", "Long"], index=0)
with col5:
    response_style = st.radio("Response Style", ["Formal", "Casual"], index=0)

# --- Language ---
language = st.radio("Select Response Language", ["English", "Arabic"], index=0)

# --- User Question ---
user_input = st.text_area("💬 Enter your question or scenario:", "")

# --- Generate AI Output ---
if st.button("🚀 Generate Suggestion") and client:
    if user_input.strip():
        # Build prompt
        prompt = f"""
        Brand: {brand}
        Behaviors: {", ".join(behaviors) if behaviors else "None"}
        Barriers: {", ".join(barriers) if barriers else "None"}
        Persona: {", ".join(persona) if persona else "None"}
        Response length: {response_length}
        Response style: {response_style}
        Language: {language}

        User Question: {user_input}
        """

        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": f"You are a helpful sales assistant chatbot that responds in {language}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            ai_output = response.choices[0].message.content

            # Save history
            st.session_state.chat_history.append({"user": user_input, "ai": ai_output})

            # Show AI output
            st.markdown("### 🤖 AI Suggestion:")
            st.write(ai_output)

        except Exception as e:
            st.error(f"⚠️ Error generating response: {e}")
    else:
        st.warning("⚠️ Please enter a question or scenario before generating.")

# --- Show Chat History ---
if st.session_state.chat_history:
    st.markdown("## 📜 Chat History")
    for i, chat in enumerate(st.session_state.chat_history):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**AI:** {chat['ai']}")
        st.markdown("---")
