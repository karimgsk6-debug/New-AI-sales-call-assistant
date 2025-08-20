import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import groq
from groq import Groq

# --- Initialize Groq client ---
client = Groq(api_key="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")

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar filters ---
st.sidebar.header("Filters")

# Brand filter
brand = st.sidebar.selectbox(
    "Select Brand",
    ["Brand A", "Brand B", "Brand C"]
)

# RACE segmentation filter
race_segment = st.sidebar.selectbox(
    "RACE Segmentation",
    ["Rookie", "Adopter", "Challenger", "Enthusiast"]
)

# Behaviors filter
behaviors = st.sidebar.multiselect(
    "Select HCP Behaviors",
    ["Scientific", "Emotional", "Data-driven", "Relationship-focused"]
)

# Barriers filter
barriers = st.sidebar.multiselect(
    "HCP Barriers",
    ["Time limitation", "Cost concerns", "Skeptical of data", "Loyal to competitor"]
)

# --- NEW: Persona filter (multiselect) ---
persona_types = st.sidebar.multiselect(
    "HCP Persona Types",
    ["Friendly", "Masked", "Most Senior", "Junior", "Scientific", "Emotional", "Analytical", "Pragmatic"]
)

# Tone of AI response
tone = st.sidebar.selectbox(
    "Response Tone",
    ["Short & Formal", "Long & Formal", "Short & Casual", "Long & Casual"]
)

# --- Chat interface ---
st.title("🧠 AI Sales Rep Mentor – Pharma Edition")

user_input = st.text_input("Ask the AI for suggestions (e.g., probing question, objection handling, call flow)...")

if st.button("Generate Suggestion") and user_input:
    # Construct dynamic prompt
    prompt = f"""
    You are a Pharma Sales AI assistant. 
    The sales rep is preparing for a visit with the following details:

    - Brand: {brand}
    - RACE Segmentation: {race_segment}
    - HCP Behaviors: {", ".join(behaviors) if behaviors else "None selected"}
    - HCP Barriers: {", ".join(barriers) if barriers else "None selected"}
    - HCP Persona Types: {", ".join(persona_types) if persona_types else "None selected"}
    - Required Tone: {tone}

    Task: Provide tailored sales call suggestions (probing questions, messaging, objection handling, or module recommendations) 
    aligned with GSK approved selling approaches.

    Sales Rep Question: {user_input}
    """

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful AI mentor for pharma sales reps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )

        ai_reply = response.choices[0].message["content"]

        # Save history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", ai_reply))

    except Exception as e:
        ai_reply = f"⚠️ Error: {e}"
        st.session_state.chat_history.append(("AI", ai_reply))

# --- Display chat history ---
st.subheader("💬 Conversation History")
for speaker, text in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"**🧑‍💼 {speaker}:** {text}")
    else:
        st.markdown(f"**🤖 {speaker}:** {text}")

