import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
import re
from groq import Groq
from difflib import get_close_matches

# --- Initialize Groq client ---
client = Groq(api_key=st.secrets["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"])

# --- Path to Shingrix PDF ---
PDF_PATH = "Test V14 per brans/SP/ TestV14 per brand/Shingrix.pdf"

# --- Extract Shingrix PDF content (text + figures + captions) ---
pdf_text = ""
pdf_figures = []  # list of dicts: {image, caption}

try:
    # Extract text
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            pdf_text += page.extract_text() or ""

    # Extract figures with nearby captions
    doc = fitz.open(PDF_PATH)
    for i, page in enumerate(doc):
        blocks = page.get_text("blocks")  # text blocks with positions
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # try to find caption text near bottom of image
            rect = fitz.Rect(page.get_image_bbox(img))
            nearby_text = ""
            for block in blocks:
                bx, by, ex, ey, _, text, *_ = block
                block_rect = fitz.Rect(bx, by, ex, ey)
                if rect.intersects(block_rect) or abs(block_rect.y0 - rect.y1) < 50:
                    nearby_text += " " + text.strip()

            pdf_figures.append({
                "image": image_bytes,
                "caption": nearby_text.strip() or f"Figure {len(pdf_figures)+1}"
            })

except Exception as e:
    st.error(f"❌ Could not process Shingrix PDF: {e}")

# --- Sidebar inputs ---
st.sidebar.header("AI Sales Call Assistant")
language = st.sidebar.selectbox("Language", ["English", "Arabic"])
segment = st.sidebar.text_input("RACE Segment")
barrier = st.sidebar.multiselect("Doctor Barrier", ["Awareness", "Access", "Cost", "Safety", "Efficacy"])
objective = st.sidebar.text_input("Objective")
specialty = st.sidebar.text_input("Doctor Specialty")
persona = st.sidebar.text_input("HCP Persona")
response_length = st.sidebar.selectbox("Response Length", ["Short", "Medium", "Long"])
response_tone = st.sidebar.selectbox("Response Tone", ["Formal", "Conversational"])

user_input = st.text_area("💬 Enter doctor question or sales scenario")

# --- Process AI response ---
if st.button("Generate Response"):
    if not user_input:
        st.warning("⚠️ Please enter a scenario/question first.")
    else:
        # Build AI prompt
        prompt = f"""
Language: {language}
User input: {user_input}
RACE Segment: {segment}
Doctor Barrier: {', '.join(barrier) if barrier else 'None'}
Objective: {objective}
Brand: Shingrix
Doctor Specialty: {specialty}
HCP Persona: {persona}

Response Length: {response_length}
Response Tone: {response_tone}

APACT (Acknowledge → Probing → Answer → Confirm → Transition) should be applied for objections.

IMPORTANT: Use the following real evidence and figures extracted from the official Shingrix leaflet:
TEXT EXCERPT:
{pdf_text[:3000]}   # limit to avoid token overload

When referring to leaflet figures, use the format: FIGURE: efficacy curve OR FIGURE: safety chart.
"""

        # Call Groq LLM
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        ai_text = response.choices[0].message.content

        # --- Display AI response ---
        st.subheader("🤖 AI Response")
        st.markdown(ai_text)

        # --- Extract Evidence ---
        evidences = re.findall(r"EVIDENCE:\s*(.*)", ai_text)
        if evidences:
            st.markdown("### 📑 Scientific Evidence")
            for ev in evidences:
                st.markdown(f"- {ev}")

        # --- Inject Figures with semantic matching ---
        figures = re.findall(r"FIGURE:\s*(.*)", ai_text)
        if figures and pdf_figures:
            st.markdown("### 📊 Figures Referenced in Response")
            for fig_req in figures:
                captions = [f["caption"] for f in pdf_figures]
                best_match = get_close_matches(fig_req.lower(), [c.lower() for c in captions], n=1, cutoff=0.3)
                if best_match:
                    idx = [c.lower() for c in captions].index(best_match[0])
                    st.image(pdf_figures[idx]["image"], caption=f"Matched to: {pdf_figures[idx]['caption']}", use_column_width=True)
                else:
                    st.warning(f"⚠️ Could not find matching figure for '{fig_req}'")
