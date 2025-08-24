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
from docx.shared import Pt

# --- Initialize Groq client securely ---
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "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"))  # fetch key from Streamlit secrets

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "filters" not in st.session_state:
    st.session_state.filters = {
        "brand": None,
        "segment": None,
        "barrier": [],
        "objective": None,
        "specialty": None,
        "persona": None,
        "personal_type_exp": [],
        "personal_type_comm": [],
        "personal_type_mind": [],
        "response_length": "Medium",
        "response_tone": "Formal",
        "interface_mode": "Chatbot",
        "max_steps": 4,
        "max_bullets": 3,
        "strict_precision": True,
    }

# --- Helpers ---
def reset_selections():
    st.session_state.filters.update({
        "brand": None,
        "segment": None,
        "barrier": [],
        "objective": None,
        "specialty": None,
        "persona": None,
        "personal_type_exp": [],
        "personal_type_comm": [],
        "personal_type_mind": [],
        "response_length": "Medium",
        "response_tone": "Formal",
        "interface_mode": "Chatbot",
        "max_steps": 4,
        "max_bullets": 3,
        "strict_precision": True,
    })

def t(lang: str, en: str, ar: str) -> str:
    return en if lang == "English" else ar

def safe_get_image(src: str, width: int = 200):
    try:
        if src.startswith("http"):
            r = requests.get(src, timeout=8)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))
        else:
            img = Image.open(src)
        st.image(img, width=width)
    except Exception:
        st.warning("⚠️ Could not load image. Using placeholder.")
        st.image("https://via.placeholder.com/200x100.png?text=No+Image", width=width)

def extract_json(s: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(s)
    except Exception:
        pass
    try:
        start = s.index("{")
        end = s.rindex("}") + 1
        return json.loads(s[start:end])
    except Exception:
        return None

def limit_list(xs: List[str], n: int) -> List[str]:
    return xs[:n] if isinstance(xs, list) else []

# --- Map response length to constraints ---
def map_len_constraints(resp_len: str):
    if resp_len == "Short":
        return 3, 2, 18
    if resp_len == "Long":
        return 6, 4, 28
    return 4, 3, 22  # Medium

# --- Render structured plan ---
def render_structured_plan(data: Dict[str, Any], lang: str):
    title = data.get("title") or t(lang, "Sales Call Plan", "خطة الزيارة")
    summary = data.get("summary") or ""
    steps = data.get("steps") or []
    closing = data.get("closing") or {}

    st.markdown(f"### {title}")
    if summary:
        st.markdown(f"> {summary}")

    for i, step in enumerate(steps, start=1):
        head = f"{t(lang, 'Step', 'الخطوة')} {i}: {step.get('title','')}"
        with st.expander(head, expanded=(i == 1)):
            for key in ["goal", "talk_track", "evidence", "objection", "action"]:
                if step.get(key):
                    st.markdown(f"**{t(lang,key.replace('_',' ').title(),'')}:** {step[key]}")
    if closing:
        st.markdown("---")
        st.markdown(f"#### {t(lang,'Closing & Next Steps','الختام والخطوات التالية')}")
        for key in ["cta","next_visit_plan"]:
            if closing.get(key):
                st.markdown(f"**{t(lang,key.replace('_',' ').title(),'')}:** {closing[key]}")
        metrics = closing.get("metrics") or []
        if metrics:
            st.markdown(f"**{t(lang,'Metrics to Track','مؤشرات للمتابعة')}:** " + " • ".join(metrics))

# --- Constants ---
gsk_brands = {
    "Augmentin": "https://assets.gskinternet.com/pharma/GSKpro/Egypt/PDFs/pi.pdf",
    "Shingrix": "https://assets.gskinternet.com/pharma/GSKpro/Saudi/shingrix/shingrix-pi.pdf",
    "Seretide": "https://assets.gskinternet.com/pharma/GSKpro/Egypt/Seretide/seretide_pi_205223.pdf",
}
gsk_brands_images = {
    "Augmentin": "https://www.bloompharmacy.com/cdn/shop/products/augmentin-1-gm-14-tablets-145727_600x600_crop_center.jpg?v=1687635056",
    "Shingrix": "https://www.oma-apteekki.fi/WebRoot/NA/Shops/na/67D6/48DA/D0B0/D959/ECAF/0A3C/0E02/D573/3ad67c4e-e1fb-4476-a8a0-873423d8db42_3Dimage.png",
    "Seretide": "https://cdn.salla.sa/QeZox/eyy7B0bg8D7a0Wwcov6UshWFc04R6H8qIgbfFq8u.png",
}
race_segments = ["R – Reach","A – Acquisition","C – Conversion","E – Engagement"]
doctor_barriers = ["1 - HCP does not consider HZ a risk","2 - No time","3 - Cost concern","4 - Not convinced","5 - Accessibility"]
objectives = ["Awareness","Adoption","Retention"]
specialties = ["General Practitioner","Cardiologist","Dermatologist","Endocrinologist","Pulmonologist"]
personas = ["Uncommitted Vaccinator","Reluctant Efficiency","Patient Influenced","Committed Vaccinator"]
personal_types_experience = ["Most Senior","Junior"]
personal_types_communication = ["Friendly","Masked","Open","Reserved"]
personal_types_mindset = ["Scientific","Emotional","Analytical","Pragmatic"]
gsk_approaches = ["Use data-driven evidence","Focus on patient outcomes","Leverage storytelling techniques"]

# --- Sidebar ---
st.sidebar.header("Filters & Options")
if st.sidebar.button("🔄 Reset All Selections"):
    reset_selections()

brand = st.sidebar.selectbox("Brand", list(gsk_brands.keys()))
segment = st.sidebar.selectbox("RACE Segment", race_segments)
barrier = st.sidebar.multiselect("Doctor Barrier", doctor_barriers)
objective = st.sidebar.selectbox("Objective", objectives)
specialty = st.sidebar.selectbox("Specialty", specialties)
persona = st.sidebar.selectbox("HCP Persona", personas)
personal_type_exp = st.sidebar.multiselect("Experience Level", personal_types_experience)
personal_type_comm = st.sidebar.multiselect("Communication Style", personal_types_communication)
personal_type_mind = st.sidebar.multiselect("Mindset", personal_types_mindset)
personal_type = personal_type_exp + personal_type_comm + personal_type_mind

response_length_options = ["Short","Medium","Long"]
response_tone_options = ["Formal","Casual","Friendly","Persuasive"]
response_length = st.sidebar.selectbox("Response Length", response_length_options)
response_tone = st.sidebar.selectbox("Response Tone", response_tone_options)

max_steps_ui = st.sidebar.slider("Max Steps", 2, 6, st.session_state.filters["max_steps"])
max_bullets_ui = st.sidebar.slider("Max Bullets/Step",1,5,st.session_state.filters["max_bullets"])
strict_precision = st.sidebar.checkbox("Strict Precision", value=st.session_state.filters["strict_precision"])
st.session_state.filters.update({"max_steps": max_steps_ui,"max_bullets": max_bullets_ui,"strict_precision": strict_precision})

interface_mode = st.sidebar.radio("Interface Mode", ["Chatbot","Card Dashboard","Flow Visualization"])

# --- Chat container ---
chat_container = st.container()
user_input = st.text_area("Type your message...", key="user_input", height=80)

# --- Prompt builder ---
def build_prompt() -> str:
    steps_limit_len, bullets_limit_len, max_words = map_len_constraints(response_length)
    steps_limit = min(steps_limit_len, st.session_state.filters["max_steps"])
    bullets_limit = min(st.session_state.filters["max_bullets"],5)

    schema = {
        "title": "string",
        "summary": "string (<=35 words)",
        "steps":[{"title":"string","goal":"string","talk_track":"string","evidence":"string","objection":"string","action":"string"}],
        "closing":{"cta":"string","next_visit_plan":"string","metrics":["string","string"]}
    }

    constraints = f"""
Return ONLY JSON matching schema. Include descriptive examples for each field.
Sort steps by highest impact first. Max {steps_limit} steps, {bullets_limit} points per field.
Language: English
"""

    approaches_str = "\n".join(gsk_approaches)
    persona_style = ", ".join(personal_type) if personal_type else "None"

    prompt = f"""
You are an expert GSK sales assistant.

Context:
- RACE Segment: {segment}
- Doctor Barriers: {', '.join(barrier) if barrier else 'None'}
- Objective: {objective}
- Brand: {brand}
- Specialty: {specialty}
- HCP Persona: {persona}
- HCP Personal Types: {persona_style}
- Response Tone: {response_tone}

Include descriptive examples for each field in your JSON output.
Approved GSK Sales Approaches:
{approaches_str}

User input:
{user_input}

{constraints}

JSON Schema:
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""
    return prompt

# --- Generate Plan ---
if st.button("🚀 Generate Plan") and user_input.strip():
    with st.spinner("Generating AI response..."):
        st.session_state.chat_history.append({"role":"user","content":user_input})
        prompt = build_prompt()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role":"system","content":"You are a helpful sales assistant."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        ai_raw = response.choices[0].message.content
        data = extract_json(ai_raw)

        st.session_state.chat_history.append({
            "role":"ai",
            "content": ai_raw if not data else json.dumps(data, ensure_ascii=False)
        })

        if data:
            st.success("Structured plan generated.")
            render_structured_plan(data,"English")

            # --- Download as Word ---
            doc = Document()
            doc.add_heading(data.get("title","Sales Call Plan"), 0)
            if data.get("summary"):
                doc.add_paragraph(data["summary"])
            for i, step in enumerate(data.get("steps",[]),1):
                doc.add_heading(f"Step {i}: {step.get('title','')}", level=1)
                for key in ["goal","talk_track","evidence","objection","action"]:
                    if step.get(key):
                        p = doc.add_paragraph(f"{key.title()}: {step[key]}")
                        p.runs[0].font.size = Pt(11)
            if data.get("closing"):
                doc.add_heading("Closing & Next Steps", level=1)
                for key in ["cta","next_visit_plan"]:
                    if data["closing"].get(key):
                        p = doc.add_paragraph(f"{key.title()}: {data['closing'][key]}")
                        p.runs[0].font.size = Pt(11)
                if data["closing"].get("metrics"):
                    p = doc.add_paragraph("Metrics: " + " • ".join(data["closing"]["metrics"]))
                    p.runs[0].font.size = Pt(11)
            doc_stream = BytesIO()
            doc.save(doc_stream)
            doc_stream.seek(0)
            st.download_button("📄 Download Plan (Word)", doc_stream, file_name="sales_call_plan.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        else:
            st.warning("Could not parse structured JSON. Showing raw output:")
            st.markdown(f"<div style='background:#f0f2f6; padding:12px; border-radius:10px'>{ai_raw}</div>", unsafe_allow_html=True)
