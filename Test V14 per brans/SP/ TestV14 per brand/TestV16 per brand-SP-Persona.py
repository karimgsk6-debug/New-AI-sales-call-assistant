import os
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from groq import Groq
import streamlit.components.v1 as components
import json
from typing import Optional, Dict, Any, List
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt

# =========================
# Load Groq API Key
# =========================
def get_groq_api_key():
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["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"]
    elif os.getenv("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"):
        return os.getenv("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")
    else:
        st.error("❌ Groq API key not found. Please set it in Streamlit Secrets or as an environment variable 'GROQ_API_KEY'.")
        st.stop()

api_key = get_groq_api_key()
client = Groq(api_key=api_key)

# =========================
# Session State
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# =========================
# UI Disclaimer
# =========================
st.markdown(
    """
    ⚠️ **Disclaimer:**  
    This is an **assistant tool** designed to support sales reps in tailoring sales calls and managing different customer types.  
    It is not a substitute for medical, legal, or compliance-approved materials. Always follow company guidelines.
    """,
    unsafe_allow_html=True
)

# =========================
# Filters
# =========================
brand = st.selectbox("Select Brand", ["", "Brand A", "Brand B", "Brand C"])
segment = st.selectbox("Select Segment (RACE)", ["", "Reach", "Act", "Convert", "Engage"])
persona = st.selectbox("Select HCP Persona", ["", "Skeptical", "Open-minded", "Busy", "Detail-oriented"])
barriers = st.multiselect("Select Barriers", ["Knowledge", "Cost concerns", "Trust", "Time", "Other"])
tone = st.selectbox("Select Response Tone", ["", "Short & Formal", "Short & Casual", "Long & Formal", "Long & Casual"])

# =========================
# Reset Filters
# =========================
if st.button("🔄 Reset Selection"):
    brand = ""
    segment = ""
    persona = ""
    barriers = []
    tone = ""

# =========================
# Chat Input
# =========================
st.markdown("### 💬 Start Discussion")
user_input = st.text_input("Enter your question or objection:", value=st.session_state.user_input)

# =========================
# Generate Response
# =========================
if st.button("Generate Response"):
    if user_input.strip() == "":
        st.warning("Please enter a question or objection.")
    else:
        full_prompt = f"""
        You are a pharma sales assistant. Follow APACT (Acknowledge, Probing, Answer, Confirm, Transition).
        Brand: {brand if brand else "N/A"}
        Segment (RACE): {segment if segment else "N/A"}
        Persona: {persona if persona else "N/A"}
        Barriers: {", ".join(barriers) if barriers else "N/A"}
        Tone: {tone if tone else "Default"}

        Customer Question/Objection: {user_input}
        """

        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": full_prompt}],
                model="llama3-70b-8192"
            )
            ai_response = response.choices[0].message.content

            # Save to history
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", ai_response))

            # Clear input box
            st.session_state.user_input = ""

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# =========================
# Display Chat History
# =========================
if st.session_state.chat_history:
    st.markdown("### 📜 Discussion History")
    for role, msg in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 AI:** {msg}")

# =========================
# New Chat
# =========================
if st.button("🆕 Start New Chat"):
    st.session_state.chat_history = []
    st.session_state.user_input = ""
    st.success("✅ New discussion started.")

# =========================
# Download Options
# =========================
if st.session_state.chat_history:
    st.markdown("### ⬇️ Download Discussion")

    if st.button("Download as Word"):
        doc = Document()
        doc.add_heading("Sales Call Assistant - Discussion", 0)
        for role, msg in st.session_state.chat_history:
            doc.add_paragraph(f"{role}: {msg}")
        doc.save("discussion.docx")
        with open("discussion.docx", "rb") as f:
            st.download_button("📄 Download Word File", f, file_name="discussion.docx")

    if st.button("Download as PPT"):
        prs = Presentation()
        slide_layout = prs.slide_layouts[1]

        for role, msg in st.session_state.chat_history:
            slide = prs.slides.add_slide(slide_layout)
            title = slide.shapes.title
            content = slide.placeholders[1]
            title.text = role
            content.text = msg

        prs.save("discussion.pptx")
        with open("discussion.pptx", "rb") as f:
            st.download_button("📊 Download PPT File", f, file_name="discussion.pptx")
