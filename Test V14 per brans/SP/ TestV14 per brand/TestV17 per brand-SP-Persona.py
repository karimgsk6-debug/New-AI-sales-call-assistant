import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from groq import Groq
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from datetime import datetime

# --- Groq API key directly in code ---
client = Groq(api_key="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")

# --- Brand PDFs dictionary (spaces encoded as %20) ---
brand_pdfs = {
    "Shingrix": "https://raw.githubusercontent.com/karimgsk6-debug/New-AI-sales-call-assistant/main/Test%20V14%20per%20brans/SP/TestV14%20per%20brand/Shingrix.pdf",
    "Trelegy": "https://raw.githubusercontent.com/karimgsk6-debug/New-AI-sales-call-assistant/main/Test%20V14%20per%20brans/SP/TestV14%20per%20brand/Trelegy.pdf",
    "Zejula": "https://raw.githubusercontent.com/karimgsk6-debug/New-AI-sales-call-assistant/main/Test%20V14%20per%20brans/SP/TestV14%20per%20brand/Zejula.pdf",
}

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_images" not in st.session_state:
    st.session_state.pdf_images = []

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
brand = st.sidebar.selectbox("Select Brand", list(brand_pdfs.keys()))
hcp_segments = st.sidebar.multiselect(
    "Select HCP Segments", 
    ["Potential", "Adopter", "Laggard", "Brand Supporter", "Competitor Supporter"]
)
hcp_barriers = st.sidebar.multiselect(
    "Select HCP Barriers", 
    ["Awareness", "Cost", "Efficacy Concerns", "Side Effects", "No Time", "Not Priority"]
)
language = st.sidebar.radio("Language", ["English", "Arabic"])
if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state.chat_history = []

st.title("💬 AI Sales Call Assistant")

# --- Load & display PDF ---
pdf_url = brand_pdfs[brand]
pdf_text = ""
st.session_state.pdf_images = []

try:
    r = requests.get(pdf_url)
    r.raise_for_status()

    if not r.content.startswith(b"%PDF"):
        st.warning("⚠️ File is not a valid PDF. Showing embedded viewer instead.")
        st.markdown(f'<iframe src="{pdf_url}" width="100%" height="600"></iframe>', unsafe_allow_html=True)
    else:
        pdf_file = BytesIO(r.content)
        pdf_reader = PdfReader(pdf_file)
        pdf_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)

        with st.expander("📑 PDF Extracted Text", expanded=False):
            st.text(pdf_text)

        # --- Extract visuals ---
        pdf_file.seek(0)
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        images = []
        for page_num in range(len(doc)):
            for img_index, img in enumerate(doc[page_num].get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                pil_img = Image.open(BytesIO(image_data))
                images.append(pil_img)
            if len(images) >= 3:  # limit to first 3 images
                break
        st.session_state.pdf_images = images

except Exception as e:
    st.error(f"⚠️ Could not fetch or parse PDF: {e}")
    st.markdown(f"👉 [Open PDF manually]({pdf_url})")

# --- Chat interface ---
user_input = st.text_input("💭 Ask your question:")

if user_input:
    prompt = f"""
You are a sales assistant helping with brand {brand}.
HCP Segments: {', '.join(hcp_segments) if hcp_segments else 'None'}
HCP Barriers: {', '.join(hcp_barriers) if hcp_barriers else 'None'}
Language: {language}
Reference PDF Text: {pdf_text[:2000]}  # limit to avoid huge context

Question: {user_input}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        answer = response.choices[0].message.content.strip()
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", answer))
    except Exception as e:
        st.error(f"❌ Chatbot error: {e}")

# --- Display chat history ---
for sender, msg in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {msg}")

# --- Display extracted visuals ---
if st.session_state.pdf_images:
    st.subheader("📊 Extracted Visuals from Leaflet")
    for img in st.session_state.pdf_images:
        st.image(img, use_container_width=True)
