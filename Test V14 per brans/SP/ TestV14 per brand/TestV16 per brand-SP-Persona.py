import os
import streamlit as st
from groq import Groq
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from io import BytesIO

# --- Disclaimer ---
st.markdown(
    "⚠️ **Disclaimer:** This assistant tool is designed to help tailor a sales call "
    "and support interactions with different customer types. It is not a replacement "
    "for your own judgment, compliance rules, or medical guidance."
)

# --- Groq API Key Handling ---
api_key = os.getenv("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")
if not api_key:
    st.warning("⚠️ Groq API key not found. Please enter it below to continue.")
    api_key = st.text_input("Enter your Groq API Key:", type="password")

client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
        st.success("✅ Groq API key loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize Groq client: {e}")

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "response" not in st.session_state:
    st.session_state.response = ""

# --- Filters ---
st.sidebar.header("🎯 Customize the Sales Call")

brand = st.sidebar.selectbox("Select Brand:", ["", "Brand A", "Brand B", "Brand C"])
segment = st.sidebar.selectbox("Select Segment (RACE):", ["", "React", "Act", "Convert", "Engage"])
persona = st.sidebar.selectbox("Select Persona:", ["", "Skeptical", "Supportive", "Busy", "Neutral"])
barriers = st.sidebar.multiselect("HCP Barriers:", ["Clinical Evidence", "Cost Concerns", "Side Effects", "Time Constraints"])
tone = st.sidebar.selectbox("Response Tone:", ["", "Short", "Long", "Formal", "Casual"])

# --- User Input ---
user_input = st.text_area("💬 Enter HCP objection, question, or discussion point:", value=st.session_state.user_input)

# --- Generate Response ---
if st.button("🚀 Generate Response") and client and user_input:
    try:
        full_prompt = (
            f"You are a pharma sales assistant. Use the APACT framework "
            f"(Acknowledge, Probing, Answer, Confirm, Transition). "
            f"Brand: {brand}, Segment: {segment}, Persona: {persona}, "
            f"Barriers: {', '.join(barriers)}, Tone: {tone}. "
            f"HCP said: {user_input}"
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": full_prompt}],
        )

        reply = response.choices[0].message.content
        st.session_state.chat_history.append(("HCP", user_input))
        st.session_state.chat_history.append(("AI", reply))
        st.session_state.response = reply
        st.session_state.user_input = ""  # clear input box

    except Exception as e:
        st.error(f"❌ Error generating response: {e}")

# --- Show Chat History ---
if st.session_state.chat_history:
    st.subheader("📝 Conversation")
    for role, message in st.session_state.chat_history:
        if role == "HCP":
            st.markdown(f"**👨‍⚕️ HCP:** {message}")
        else:
            st.markdown(f"**🤖 Assistant:** {message}")

# --- Download as Word ---
if st.session_state.response:
    def create_word(response_text):
        doc = Document()
        doc.add_heading("AI Sales Assistant Response", level=1)
        doc.add_paragraph(response_text)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    word_buffer = create_word(st.session_state.response)
    st.download_button(
        label="📥 Download as Word",
        data=word_buffer,
        file_name="Sales_Assistant_Response.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # --- Download as PPT ---
    def create_ppt(response_text):
        prs = Presentation()
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        content = slide.placeholders[1]
        title.text = "AI Sales Assistant Response"
        content.text = response_text
        buffer = BytesIO()
        prs.save(buffer)
        buffer.seek(0)
        return buffer

    ppt_buffer = create_ppt(st.session_state.response)
    st.download_button(
        label="📊 Download as PowerPoint",
        data=ppt_buffer,
        file_name="Sales_Assistant_Response.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

# --- Reset Filters ---
if st.sidebar.button("🔄 Reset Filters"):
    st.session_state.chat_history = []
    st.session_state.user_input = ""
    st.session_state.response = ""
    st.experimental_rerun()

# --- Start New Discussion ---
if st.button("🆕 Start New Discussion"):
    st.session_state.chat_history = []
    st.session_state.user_input = ""
    st.session_state.response = ""
    st.experimental_rerun()
