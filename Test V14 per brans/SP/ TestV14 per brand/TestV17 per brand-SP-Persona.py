import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from groq import Groq
import streamlit.components.v1 as components
import os
from PyPDF2 import PdfReader

# --- Initialize Groq client (API key directly in code) ---
client = Groq(api_key="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")

# --- Brand PDFs dictionary ---
brand_pdfs = {
    "Shingrix": "https://raw.githubusercontent.com/karimgsk6-debug/New-AI-sales-call-assistant/main/Test V14_per_brans/SP/Test V14_per_brand/Shingrix.pdf",
    "Trelegy": "https://raw.githubusercontent.com/karimgsk6-debug/New-AI-sales-call-assistant/main/TestV14_per_brans/SP/TestV14_per_brand/Trelegy.pdf",
    "Zejula": "https://raw.githubusercontent.com/karimgsk6-debug/New-AI-sales-call-assistant/main/TestV14_per_brans/SP/TestV14_per_brand/Zejula.pdf",
}

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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

# --- Load & Display Brand PDF ---
pdf_url = brand_pdfs[brand]

try:
    r = requests.get(pdf_url)
    r.raise_for_status()

    if not r.content.startswith(b"%PDF"):
        st.warning("⚠️ File is not a valid PDF. Showing embedded viewer instead.")
        st.markdown(f'<iframe src="{pdf_url}" width="100%" height="600"></iframe>', unsafe_allow_html=True)
        pdf_text = ""
    else:
        pdf_file = BytesIO(r.content)
        pdf_reader = PdfReader(pdf_file)
        pdf_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)

        with st.expander("📑 PDF Extracted Text", expanded=False):
            st.text(pdf_text)

except Exception as e:
    st.error(f"⚠️ Could not fetch or parse PDF: {e}")
    st.markdown(f"👉 [Open PDF manually]({pdf_url})")
    pdf_text = ""

# --- Chatbot interface ---
user_input = st.text_input("💭 Ask your question:")

if user_input:
    # Build prompt
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

        # Append to history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", answer))

    except Exception as e:
        st.error(f"❌ Chatbot error: {e}")

# --- Display chat history ---
for sender, msg in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {msg}")
