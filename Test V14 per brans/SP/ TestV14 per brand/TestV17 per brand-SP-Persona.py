# app.py
import os
import re
import base64
from io import BytesIO
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image

# --- Optional deps (graceful fallback if missing) ---
try:
    from docx import Document
    DOCX_OK = True
except Exception:
    DOCX_OK = False

try:
    from groq import Groq
    GROQ_OK = True
except Exception:
    GROQ_OK = False

# =========================
# Configuration & Constants
# =========================
st.set_page_config(page_title="AI Sales Call Assistant", layout="wide")

BASE_DIR = Path(__file__).parent

# Brand PDFs
BRAND_PDFS = {
    "Shingrix": BASE_DIR / "assets" / "PDFs" / "Shingrix.pdf",
    "Trelegy":  BASE_DIR / "assets" / "PDFs" / "Trelegy.pdf",
    "Zejula":   BASE_DIR / "assets" / "PDFs" / "Zejula.pdf",
}

# Visual library per brand (keywords → image path)
VISUALS = {
    "Shingrix": {
        "cost":       BASE_DIR / "assets" / "Visuals" / "Shingrix" / "cost_benefit.png",
        "efficacy":   BASE_DIR / "assets" / "Visuals" / "Shingrix" / "efficacy_chart.png",
        "safety":     BASE_DIR / "assets" / "Visuals" / "Shingrix" / "safety_profile.png",
        "adherence":  BASE_DIR / "assets" / "Visuals" / "Shingrix" / "adherence_curve.png",
    },
    "Trelegy": {
        "cost":       BASE_DIR / "assets" / "Visuals" / "Trelegy" / "cost_benefit.png",
        "efficacy":   BASE_DIR / "assets" / "Visuals" / "Trelegy" / "efficacy_chart.png",
        "safety":     BASE_DIR / "assets" / "Visuals" / "Trelegy" / "safety_profile.png",
        "adherence":  BASE_DIR / "assets" / "Visuals" / "Trelegy" / "adherence_curve.png",
    },
    "Zejula": {
        "cost":       BASE_DIR / "assets" / "Visuals" / "Zejula" / "cost_benefit.png",
        "efficacy":   BASE_DIR / "assets" / "Visuals" / "Zejula" / "efficacy_chart.png",
        "safety":     BASE_DIR / "assets" / "Visuals" / "Zejula" / "safety_profile.png",
        "adherence":  BASE_DIR / "assets" / "Visuals" / "Zejula" / "adherence_curve.png",
    },
}

HCP_SEGMENTS = [
    "R – Reach",
    "A – Acquisition",
    "C – Conversion",
    "E – Engagement",
]

HCP_PERSONAS = [
    "Uncommitted Vaccinator – Not engaged, poor knowledge, least likely to prescribe vaccines (26%)",
    "Reluctant Efficiency – Do not see vaccinating 50+ as part of role, least likely to believe in impact (12%)",
    "Patient Influenced – Aware of benefits but prescribes only if patient requests (26%)",
    "Committed Vaccinator – Very positive, motivated, prioritizes vaccination & sets example (36%)"
]

DOCTOR_BARRIERS = [
    "Cost",
    "Efficacy",
    "Safety",
    "Adherence",
    "Time constraints",
    "Risk perception (patient not at risk)",
    "Access / logistics",
]

SALES_CALL_FLOW = ["Prepare", "Engage", "Create Opportunities", "Influence", "Drive Impact", "Post Call Analysis"]

# ======================
# Utilities / Formatting
# ======================
def bold_and_separate_apact(text: str) -> str:
    """
    Ensures APACT step headers are bold + separated lines.
    If already present, it just strengthens formatting.
    """
    # Normalize newlines
    t = text.replace("\r\n", "\n")

    # Add line breaks after headers and ensure bold
    steps = ["Acknowledge", "Probing", "Answer", "Confirm", "Transition"]
    for step in steps:
        # Make header bold and ensure it starts on its own line
        t = re.sub(rf"(?i)\b{step}\b\s*:?","**"+step+"**:\n", t)

    # Ensure a clear blank line between steps
    for step in steps:
        t = t.replace(f"**{step}**:\n", f"**{step}**:\n")

    return t

def embed_pdf(pdf_path: Path, height: int = 520):
    if pdf_path and pdf_path.exists():
        with open(pdf_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" '
            f'width="100%" height="{height}" type="application/pdf"></iframe>',
            unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ PDF not found at: {pdf_path}")

def pick_visual_keywords(ai_text: str, selected_barriers: list[str]) -> set[str]:
    """
    Collect visual keywords from AI text and user-selected barriers.
    """
    text = (ai_text or "").lower()
    keys = set()

    # From AI response content
    for kw in ["cost", "efficacy", "safety", "adherence"]:
        if kw in text:
            keys.add(kw)

    # From barriers
    for b in selected_barriers:
        b_low = b.lower()
        if "cost" in b_low:
            keys.add("cost")
        if "efficacy" in b_low:
            keys.add("efficacy")
        if "safety" in b_low:
            keys.add("safety")
        if "adherence" in b_low:
            keys.add("adherence")

    return keys

def groq_generate_apact_reply(client, payload: str) -> str:
    """
    Calls Groq; if not configured/available, returns a safe APACT template.
    """
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful, compliant pharma sales assistant. Use APACT for objections."},
                {"role": "user", "content": payload}
            ],
            temperature=0.6
        )
        content = resp.choices[0].message["content"]
        return content
    except Exception as e:
        # Fallback APACT template
        return (
            "**Acknowledge**:\n"
            "I understand this is an important consideration for your practice.\n\n"
            "**Probing**:\n"
            "Could you share what specifically concerns you most—cost to patients, comparative efficacy, or safety in certain profiles?\n\n"
            "**Answer**:\n"
            "Based on the core evidence and label, the product addresses these points by… (insert brand PDF data and approved claims).\n\n"
            "**Confirm**:\n"
            "Does this address the main concern for your typical patient population?\n\n"
            "**Transition**:\n"
            "If so, we can discuss a simple way to identify eligible patients and streamline the next steps."
        )

# ======================
# Sidebar / Top Controls
# ======================
st.title("🧠 AI Sales Call Assistant")

top1, top2, top3, top4 = st.columns([2, 2, 2, 2])
with top1:
    brand = st.selectbox("Product", list(BRAND_PDFS.keys()))
with top2:
    segment = st.selectbox("RACE Segment", HCP_SEGMENTS)
with top3:
    persona = st.selectbox("HCP Persona", HCP_PERSONAS)
with top4:
    barriers = st.multiselect("Barriers", DOCTOR_BARRIERS, default=[])

# Store chat in session
if "chat" not in st.session_state:
    st.session_state.chat = []  # list of dicts: {"role": "user"/"ai", "content": "...", "time": "HH:MM"}

# ======================
# Chat UI (WhatsApp-ish)
# ======================
st.markdown("### 💬 Chat")

with st.form("chat_form", clear_on_submit=True):
    c1, c2 = st.columns([12, 1])
    user_msg = c1.text_input("Type your message…", key="chat_input")
    sent = c2.form_submit_button("➤")  # send icon button

if sent and user_msg.strip():
    st.session_state.chat.append({"role": "user", "content": user_msg, "time": datetime.now().strftime("%H:%M")})

    # Build prompt for Groq (APACT enforced)
    prompt = f"""
Brand: {brand}
RACE Segment: {segment}
HCP Persona: {persona}
Barriers: {", ".join(barriers) if barriers else "None"}

User message: {user_msg}

Requirements:
- Use APACT (Acknowledge → Probing → Answer → Confirm → Transition).
- Put each APACT step on its own line with the step name in ALL CAPS or Title Case at the start.
- Keep content compliant and non-promotional; only use on-label, approved claims that would exist in the brand PDF.
- Keep it concise and practical for a live sales call.
"""

    # Create Groq client if possible
    ai_text_raw = None
    if GROQ_OK and os.getenv("GROQ_API_KEY", "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"):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        ai_text_raw = groq_generate_apact_reply(client, prompt)
    else:
        ai_text_raw = groq_generate_apact_reply(None, prompt)

    # Post-process to ensure APACT formatting is bold + separated
    ai_text = bold_and_separate_apact(ai_text_raw)
    st.session_state.chat.append({"role": "ai", "content": ai_text, "time": datetime.now().strftime("%H:%M")})

# Render chat bubbles
bubble_html = ""
for m in st.session_state.chat:
    content_html = m["content"].replace("\n", "<br>")
    if m["role"] == "user":
        bubble_html += f"""
        <div style='text-align:right; background:#dcf8c6; padding:10px;
        border-radius:15px; margin:6px; display:inline-block; max-width:85%'>
          {content_html}<br>
          <span style='font-size:10px;color:#667'>{m["time"]}</span>
        </div><br>
        """
    else:
        bubble_html += f"""
        <div style='text-align:left; background:#f0f2f6; padding:12px;
        border-radius:15px; margin:6px; display:inline-block; max-width:85%'>
          {content_html}<br>
          <span style='font-size:10px;color:#667'>{m["time"]}</span>
        </div><br>
        """
st.markdown(bubble_html, unsafe_allow_html=True)

# ======================
# PDF Preview (Embedded)
# ======================
st.markdown("### 📄 Product PDF")
embed_pdf(BRAND_PDFS[brand])

# ======================
# Dynamic Visual Aids (below PDF)
# ======================
st.markdown("### 🖼️ Relevant Visual Aids")
last_ai_msg = next((m["content"] for m in reversed(st.session_state.chat) if m["role"] == "ai"), "")
wanted = pick_visual_keywords(last_ai_msg, barriers)

brand_visuals = VISUALS.get(brand, {})
shown_any = False

# If no keywords detected yet (e.g., first message), you can default to efficacy & safety
if not wanted:
    wanted = {"efficacy", "safety"}

# Show each relevant visual if it exists
cols = st.columns(2)
i = 0
for kw in sorted(wanted):
    img_path = brand_visuals.get(kw)
    if img_path and img_path.exists():
        with cols[i % 2]:
            try:
                st.image(str(img_path), caption=f"{brand} – {kw.capitalize()} Aid", use_container_width=True)
                shown_any = True
            except Exception:
                st.warning(f"⚠️ Could not render image: {img_path.name}")
        i += 1

if not shown_any:
    st.info("No relevant visuals available for this context. Add images to the brand’s Visuals folder to enable this panel.")

# ======================
# Word Download (outside form)
# ======================
st.markdown("---")
if DOCX_OK and st.session_state.chat:
    doc = Document()
    doc.add_heading("AI Sales Call Assistant", 0)
    doc.add_paragraph(f"Brand: {brand}")
    doc.add_paragraph(f"RACE Segment: {segment}")
    doc.add_paragraph(f"HCP Persona: {persona}")
    doc.add_paragraph("Barriers: " + (", ".join(barriers) if barriers else "None"))
    doc.add_paragraph("Sales Call Flow: " + " → ".join(SALES_CALL_FLOW))

    doc.add_heading("Conversation", level=1)
    for m in st.session_state.chat:
        doc.add_heading(("User" if m["role"] == "user" else "AI") + f" ({m['time']})", level=2)
        doc.add_paragraph(m["content"])

    # Save to buffer
    word_buf = BytesIO()
    doc.save(word_buf)
    word_buf.seek(0)

    st.download_button(
        "📥 Download as Word (.docx)",
        data=word_buf.getvalue(),
        file_name=f"{brand}_Sales_Call_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
else:
    if not DOCX_OK:
        st.warning("⚠️ python-docx not installed — Word export disabled. Install with: pip install python-docx")
