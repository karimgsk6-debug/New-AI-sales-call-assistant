import streamlit as st
from PIL import Image
import requests
from io import BytesIO, BytesIO as io_bytes
import groq
from groq import Groq
from datetime import datetime

# --- Optional dependency for Word download ---
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    st.warning("⚠️ python-docx not installed. Word download unavailable.")

# --- Optional dependencies for PDF ---
try:
    import PyPDF2
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    st.warning("⚠️ PyPDF2 or PyMuPDF not installed. PDF upload features are disabled.")

# --- Initialize Groq client ---
client = Groq(api_key="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")  # replace with your key

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_images" not in st.session_state:
    st.session_state.pdf_images = []

# --- Language selection ---
language = st.radio("Select Language / اختر اللغة", options=["English", "العربية"])

# --- Upload PDF (optional) ---
if PDF_AVAILABLE:
    uploaded_pdf = st.file_uploader("📑 Upload Medical PDF", type=["pdf"])
    if uploaded_pdf:
        # Extract text
        try:
            reader = PyPDF2.PdfReader(uploaded_pdf)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n"
            st.session_state.pdf_text = pdf_text[:6000]  # limit for AI prompt
        except Exception as e:
            st.warning(f"⚠️ Could not read PDF text: {e}")
            st.session_state.pdf_text = ""

        # Extract images
        try:
            pdf_images = []
            doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
            for page_num in range(len(doc)):
                for img_index, img in enumerate(doc[page_num].get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_data = base_image["image"]
                    pdf_images.append(Image.open(BytesIO(image_data)))
                if len(pdf_images) >= 3:  # show first 3 images
                    break
            st.session_state.pdf_images = pdf_images
        except Exception as e:
            st.warning(f"⚠️ Could not extract images from PDF: {e}")
            st.session_state.pdf_images = []
else:
    st.session_state.pdf_text = ""
    st.session_state.pdf_images = []

# --- GSK Logo ---
logo_fallback_url = "https://www.tungsten-network.com/wp-content/uploads/2020/05/GSK_Logo_Full_Colour_RGB.png"
st.image(logo_fallback_url, width=150)
st.title("🧠 AI Sales Call Assistant")

# --- Filters ---
race_segments = ["R – Reach", "A – Acquisition", "C – Conversion", "E – Engagement"]
doctor_barriers = ["HCP does not consider HZ as risk", "No time", "Cost", "Not convinced effective", "Accessibility issues"]
objectives = ["Awareness", "Adoption", "Retention"]
specialties = ["GP", "Cardiologist", "Dermatologist", "Endocrinologist", "Pulmonologist"]
personas = ["Uncommitted Vaccinator", "Reluctant Efficiency", "Patient Influenced", "Committed Vaccinator"]
gsk_approaches = ["Use data-driven evidence", "Focus on patient outcomes", "Leverage storytelling techniques"]
sales_call_flow = ["Prepare", "Engage", "Create Opportunities", "Influence", "Drive Impact", "Post Call Analysis"]

# --- Sidebar filters ---
st.sidebar.header("Filters & Options")
brand = st.sidebar.selectbox("Select Brand", options=["Shingrix", "Trelegy", "Zejula"])
segment = st.sidebar.selectbox("Select RACE Segment", race_segments)
barrier = st.sidebar.multiselect("Select Doctor Barrier", doctor_barriers, default=[])
objective = st.sidebar.selectbox("Select Objective", objectives)
specialty = st.sidebar.selectbox("Select Doctor Specialty", specialties)
persona = st.sidebar.selectbox("Select HCP Persona", personas)
response_length = st.sidebar.selectbox("Response Length", ["Short", "Medium", "Long"])
response_tone = st.sidebar.selectbox("Response Tone", ["Formal", "Casual", "Friendly", "Persuasive"])

# --- Chat input ---
st.subheader("💬 Chatbot Interface")
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message...")
    submitted = st.form_submit_button("➤")

if submitted and user_input.strip():
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input, "time": datetime.now().strftime("%H:%M")}
    )

    # Include PDF text if available
    pdf_context = st.session_state.pdf_text if st.session_state.pdf_text else "No leaflet uploaded."

    prompt = f"""
Language: {language}
User Input: {user_input}
Brand: {brand}
Objective: {objective}
RACE Segment: {segment}
Doctor Barriers: {', '.join(barrier) if barrier else 'None'}
Specialty: {specialty}
Persona: {persona}

--- Medical Information (from uploaded leaflet) ---
{pdf_context[:3000]}

--- Instructions ---
Use APACT method (Acknowledge → Probing → Answer → Confirm → Transition).
Provide practical sales call suggestions aligned with the leaflet.
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": f"You are a helpful sales assistant chatbot in {language}."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    ai_output = response.choices[0].message.content
    st.session_state.chat_history.append(
        {"role": "ai", "content": ai_output, "time": datetime.now().strftime("%H:%M")}
    )

# --- Display chat ---
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"🧑‍💼 **You:** {msg['content']}")
    else:
        st.markdown(f"🤖 **AI:** {msg['content']}")

# --- Show PDF visuals ---
if st.session_state.pdf_images:
    st.subheader("📊 Extracted Visuals from PDF")
    for img in st.session_state.pdf_images:
        st.image(img, use_container_width=True)

# --- Word download ---
if DOCX_AVAILABLE and st.session_state.chat_history:
    latest_ai = [msg["content"] for msg in st.session_state.chat_history if msg["role"] == "ai"]
    if latest_ai:
        doc = Document()
        doc.add_heading("AI Sales Call Response", 0)
        doc.add_paragraph(latest_ai[-1])
        word_buffer = io_bytes()
        doc.save(word_buffer)
        st.download_button("📥 Download as Word (.docx)", word_buffer.getvalue(), file_name="AI_Response.docx")
