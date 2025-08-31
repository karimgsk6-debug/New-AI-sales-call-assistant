import streamlit as st
from datetime import datetime

# -------------------------
# Dependency checks
# -------------------------
missing_libs = []
try:
    from PIL import Image
except ImportError:
    missing_libs.append("Pillow")
try:
    import requests
except ImportError:
    missing_libs.append("requests")
try:
    from groq import Groq
except ImportError:
    missing_libs.append("groq")
try:
    import fitz  # PyMuPDF
except ImportError:
    missing_libs.append("PyMuPDF")
try:
    import pdfplumber
except ImportError:
    missing_libs.append("pdfplumber")
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    missing_libs.append("scikit-learn")
try:
    from io import BytesIO, BytesIO as io_bytes
except ImportError:
    missing_libs.append("io (standard library)")
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    missing_libs.append("python-docx")

if missing_libs:
    st.warning(f"⚠️ The following Python libraries are missing: {', '.join(missing_libs)}\nPlease install them via requirements.txt or pip.")
    st.stop()

# -------------------------
# App Title & Logo
# -------------------------
st.title("🧠 Shingrix AI Sales Call Assistant with Evidence & Figures")
logo_url = "https://www.tungsten-network.com/wp-content/uploads/2020/05/GSK_Logo_Full_Colour_RGB.png"
st.image(logo_url, width=120)

# -------------------------
# Groq API
# -------------------------
GROQ_API_KEY = "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"  # Replace with your Groq API key
SELECTED_MODEL = "YOUR_VALID_MODEL_NAME_HERE"  # Replace with a valid model
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"⚠️ Could not initialize Groq client: {e}")
    st.stop()

# -------------------------
# Brand PDF
# -------------------------
pdf_path = "Test V14 per brans/SP/ TestV14 per brand/Shingrix.pdf"
pdf_text, pdf_figures = "", []

import fitz
import pdfplumber
import base64

try:
    # Extract text
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pdf_text += page.extract_text() or ""
    pdf_text_truncated = pdf_text[:2000]

    # Extract figures + captions
    doc = fitz.open(pdf_path)
    for page in doc:
        blocks = page.get_text("blocks")
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            rect = fitz.Rect(page.get_image_bbox(img))
            caption_text = ""
            for block in blocks:
                bx, by, ex, ey, _, text, *_ = block
                block_rect = fitz.Rect(bx, by, ex, ey)
                if rect.intersects(block_rect) or abs(block_rect.y0 - rect.y1) < 50:
                    if isinstance(text, str):
                        caption_text += " " + text.strip()
            caption_text = caption_text.strip() or f"Figure {len(pdf_figures)+1}"
            pdf_figures.append({"image": img_bytes, "caption": caption_text})
    st.success("✅ Shingrix PDF loaded with text and figures.")
except Exception as e:
    st.warning(f"⚠️ Could not process Shingrix PDF: {e}")

# -------------------------
# Chat session state
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("Filters & Options")
language = st.sidebar.radio("Select Language / اختر اللغة", ["English", "العربية"])
race_segments = [
    "R – Reach", "A – Acquisition", "C – Conversion", "E – Engagement"
]
doctor_barriers = [
    "HCP does not consider HZ as risk", "No time to discuss preventive measures",
    "Cost considerations", "Not convinced HZ Vx effective", "Accessibility issues"
]
objectives = ["Awareness", "Adoption", "Retention"]
specialties = ["GP", "Cardiologist", "Dermatologist", "Endocrinologist", "Pulmonologist"]
personas = ["Uncommitted Vaccinator", "Reluctant Efficiency", "Patient Influenced", "Committed Vaccinator"]

brand = st.sidebar.selectbox("Brand", ["Shingrix"])
segment = st.sidebar.selectbox("RACE Segment", race_segments)
barrier = st.sidebar.multiselect("Doctor Barrier", doctor_barriers)
objective = st.sidebar.selectbox("Objective", objectives)
specialty = st.sidebar.selectbox("Doctor Specialty", specialties)
persona = st.sidebar.selectbox("HCP Persona", personas)
response_length = st.sidebar.selectbox("Response Length", ["Short", "Medium", "Long"])
response_tone = st.sidebar.selectbox("Response Tone", ["Formal", "Casual", "Friendly", "Persuasive"])

# -------------------------
# Display chat
# -------------------------
st.subheader("💬 Chatbot Interface")
chat_placeholder = st.empty()

def display_chat(selected_figures=None):
    chat_html = ""
    for msg in st.session_state.chat_history:
        time = msg.get("time", "")
        content = msg["content"].replace("\n","<br>")
        if selected_figures:
            for f in selected_figures:
                caption = f["caption"]
                img_bytes = f["image"]
                img_html = f'<img src="data:image/png;base64,{base64.b64encode(img_bytes).decode()}" width="400"/>'
                content = content.replace(caption, f"{caption}<br>{img_html}")
        if msg["role"]=="user":
            chat_html += f"<div style='text-align:right; background:#dcf8c6; padding:10px; border-radius:15px; margin:5px; display:inline-block; max-width:80%;'>{content}<br><span style='font-size:10px; color:gray;'>{time}</span></div>"
        else:
            chat_html += f"<div style='text-align:left; background:#f0f2f6; padding:10px; border-radius:15px; margin:5px; display:inline-block; max-width:80%;'>{content}<br><span style='font-size:10px; color:gray;'>{time}</span></div>"
    chat_placeholder.markdown(chat_html, unsafe_allow_html=True)

display_chat()

# -------------------------
# Chat input form
# -------------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message...", key="user_input_box")
    submitted = st.form_submit_button("➤")

if submitted and user_input.strip():
    st.session_state.chat_history.append({"role":"user","content":user_input,"time":datetime.now().strftime("%H:%M")})

    # -------------------------
    # Select relevant figures
    # -------------------------
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    def select_relevant_figures(user_query, figures, top_k=2):
        if not figures: return []
        captions = [f["caption"] for f in figures]
        corpus = captions + [user_query]
        vectorizer = TfidfVectorizer().fit_transform(corpus)
        similarity = cosine_similarity(vectorizer[-1:], vectorizer[:-1])
        top_indices = similarity[0].argsort()[::-1][:top_k]
        return [figures[i] for i in top_indices]

    selected_figures = select_relevant_figures(user_input, pdf_figures, top_k=2)

    # -------------------------
    # Prepare AI prompt
    # -------------------------
    gsk_approaches = ["Use data-driven evidence","Focus on patient outcomes","Leverage storytelling techniques"]
    sales_call_flow = ["Prepare", "Engage", "Create Opportunities", "Influence", "Drive Impact", "Post Call Analysis"]

    approaches_str = "\n".join(gsk_approaches)
    flow_str = " → ".join(sales_call_flow)
    figure_texts = "\n".join([f"{i+1}. {f['caption']}" for i,f in enumerate(selected_figures)])

    prompt = f"""
Language: {language}
User input: {user_input}
RACE Segment: {segment}
Doctor Barrier: {', '.join(barrier) if barrier else 'None'}
Objective: {objective}
Brand: {brand}
Doctor Specialty: {specialty}
HCP Persona: {persona}
Approved Sales Approaches:
{approaches_str}
Sales Call Flow Steps:
{flow_str}
Leaflet Evidence (truncated):
{pdf_text[:2000]}
Include relevant figures (captions only) in your response:
{figure_texts}
Response Length: {response_length}
Response Tone: {response_tone}
Use APACT technique (Acknowledge→Probing→Answer→Confirm→Transition) for handling objections.
"""

    # -------------------------
    # Safe Groq API call
    # -------------------------
    try:
        response = client.chat.completions.create(
            model=SELECTED_MODEL,
            messages=[
                {"role":"system","content":f"You are a helpful sales assistant chatbot that responds in {language}."},
                {"role":"user","content":prompt}
            ],
            temperature=0.7
        )
        ai_output = response.choices[0].message.content
    except Exception as e:
        ai_output = f"⚠️ Error calling Groq API:\n{e}"

    st.session_state.chat_history.append({"role":"ai","content":ai_output,"time":datetime.now().strftime("%H:%M")})
    display_chat(selected_figures=selected_figures)

# -------------------------
# Word export
# -------------------------
if DOCX_AVAILABLE and st.session_state.chat_history:
    latest_ai = [msg["content"] for msg in st.session_state.chat_history if msg["role"]=="ai"]
    if latest_ai:
        doc = Document()
        doc.add_heading("AI Sales Call Response", 0)
        doc.add_paragraph(latest_ai[-1])
        word_buffer = io_bytes()
        doc.save(word_buffer)
        st.download_button("📥 Download as Word (.docx)", word_buffer.getvalue(), file_name="AI_Response.docx")

# -------------------------
# PDF Leaflet link
# -------------------------
st.markdown(f"[Brand Leaflet - {brand}]({pdf_path})")
