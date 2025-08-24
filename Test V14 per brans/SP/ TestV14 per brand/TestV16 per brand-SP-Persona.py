import streamlit as st
from groq import Groq
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

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

# --- Add Company Logo ---
logo_url = "https://upload.wikimedia.org/wikipedia/commons/3/3f/GSK_logo_2022.svg"  # official GSK logo
st.image(logo_url, width=150)
st.title("🧠 AI Sales Call Assistant")
st.markdown("Prepare for HCP visits with AI-powered suggestions tailored to persona, behaviors, and barriers.")
st.markdown("---")

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

    # --- Export options ---
    st.subheader("📥 Export Chat History")

    # TXT Export
    chat_text = "\n\n".join([f"You: {c['user']}\nAI: {c['ai']}" for c in st.session_state.chat_history])
    st.download_button("⬇️ Download as TXT", chat_text, file_name="chat_history.txt")

    # PDF Export
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    y = height - 60

    # Add Logo & Header to PDF
    try:
        logo = ImageReader(logo_url)
        pdf.drawImage(logo, 40, height - 80, width=80, preserveAspectRatio=True, mask='auto')
    except Exception:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(40, height - 50, "GSK Sales Assistant")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(150, height - 50, "AI Sales Call Assistant - Chat History")

    # Add chat history
    pdf.setFont("Helvetica", 10)
    for chat in st.session_state.chat_history:
        text = f"You: {chat['user']}\nAI: {chat['ai']}\n"
        for line in text.split("\n"):
            pdf.drawString(40, y, line)
            y -= 14
            if y < 40:  # new page
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = height - 40
        y -= 10

    pdf.save()
    pdf_buffer.seek(0)

    st.download_button(
        "⬇️ Download as PDF",
        data=pdf_buffer,
        file_name="chat_history.pdf",
        mime="application/pdf"
    )
