import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import groq
from groq import Groq
import streamlit.components.v1 as components
import json
from typing import Optional, Dict, Any, List
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from io import BytesIO

# --- Initialize Groq client ---
client = Groq(api_key="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")  # Replace with your real key

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# --- Title ---
st.title("💊 AI Sales Call Assistant (APACT Model)")

# --- Filters ---
brand = st.selectbox("Select Brand", ["Brand A", "Brand B", "Brand C"])
segment = st.selectbox("Select HCP Segment", ["Rookie", "Engager", "Advocate", "Challenger"])
persona = st.selectbox("Select HCP Persona", ["Scientific", "Practical", "Skeptical", "Open-Minded"])
barriers = st.multiselect("Select HCP Barriers", ["Lack of awareness", "Trust issues", "Preference for competitors", "Cost concerns"])

tone = st.selectbox("Response Tone", ["Short & Formal", "Short & Casual", "Long & Formal", "Long & Casual"])
language = st.selectbox("Language", ["English", "Arabic"])

# --- APACT Technique Helper ---
def format_apact_response(response_text: str, lang: str) -> str:
    if lang == "Arabic":
        return f"""
✅ **Acknowledge (الاعتراف):** {response_text}

🔍 **Probing (الاستقصاء):** [اسأل سؤالًا لفهم موقف الطبيب]

💡 **Answer (الإجابة):** [قدّم استجابة مقنعة]

✅ **Confirm (التأكيد):** [تحقق من موافقة الطبيب]

🔄 **Transition (الانتقال):** [انتقل إلى النقطة التالية]
"""
    else:
        return f"""
✅ **Acknowledge:** {response_text}

🔍 **Probing:** [Ask a question to understand HCP’s perspective]

💡 **Answer:** [Provide a clear and convincing response]

✅ **Confirm:** [Check HCP’s agreement]

🔄 **Transition:** [Move to the next discussion step]
"""

# --- Chatbot UI ---
st.subheader("💬 Discussion")

for i, (role, message) in enumerate(st.session_state.chat_history):
    if role == "user":
        st.markdown(f"👤 **You:** {message}")
    else:
        st.markdown(f"🤖 **Assistant:** {message}")

# --- Input box ---
placeholder_text = "Type your question or objection here..."
user_input = st.text_area(
    placeholder_text,
    key="chat_input",
    height=80,
    value=st.session_state.user_input
)

# --- Send button ---
if st.button("Send"):
    if user_input.strip():
        # Add user input to history
        st.session_state.chat_history.append(("user", user_input))

        # Call Groq API
        prompt = f"""
        Brand: {brand}
        Segment: {segment}
        Persona: {persona}
        Barriers: {", ".join(barriers)}
        Tone: {tone}
        Language: {language}

        User said: {user_input}

        Respond using APACT model.
        """

        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile"
            )

            ai_reply = response.choices[0].message.content
            formatted_reply = format_apact_response(ai_reply, language)

            # Add assistant response to history
            st.session_state.chat_history.append(("assistant", formatted_reply))

        except Exception as e:
            st.error(f"Error: {str(e)}")

        # Clear input after sending
        st.session_state.user_input = ""
        st.rerun()

# --- Start new discussion button ---
if st.button("🆕 Start New Discussion"):
    st.session_state.chat_history = []
    st.session_state.user_input = ""
    st.rerun()

# --- Download options ---
st.subheader("📥 Download Conversation")

def export_to_word(history):
    doc = Document()
    doc.add_heading("AI Sales Call Assistant - APACT Conversation", 0)
    for role, message in history:
        if role == "user":
            doc.add_paragraph(f"You: {message}", style="Normal")
        else:
            doc.add_paragraph(f"Assistant:\n{message}", style="Normal")
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def export_to_ppt(history):
    prs = Presentation()
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = "AI Sales Call Assistant"
    slide.placeholders[1].text = "APACT Conversation Export"

    for role, message in history:
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = f"{role.capitalize()}"
        slide.placeholders[1].text = message

    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer

col1, col2 = st.columns(2)

with col1:
    if st.session_state.chat_history:
        word_file = export_to_word(st.session_state.chat_history)
        st.download_button("⬇️ Download as Word", data=word_file,
                           file_name="APACT_Conversation.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

with col2:
    if st.session_state.chat_history:
        ppt_file = export_to_ppt(st.session_state.chat_history)
        st.download_button("⬇️ Download as PPT", data=ppt_file,
                           file_name="APACT_Conversation.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
