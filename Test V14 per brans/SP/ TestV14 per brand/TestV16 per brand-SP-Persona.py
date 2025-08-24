import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import groq
from groq import Groq
import streamlit.components.v1 as components
import json
from typing import Optional, Dict, Any, List

# --- Initialize Groq client ---
client = Groq(api_key="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")  # <-- Add your API key here

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
        # Fallback: extract largest JSON-like substring
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(s[start:end+1])
            except Exception:
                return None
    return None

def limit_list(xs: List[str], n: int) -> List[str]:
    return xs[:n] if isinstance(xs, list) else []

def render_structured_plan(data: Dict[str, Any], lang: str):
    title = data.get("title") or t(lang, "Sales Call Plan", "خطة الزيارة")
    summary = data.get("summary") or ""
    steps = data.get("steps") or []
    closing = data.get("closing") or {}

    st.markdown(f"### {title}")
    if summary:
        st.markdown(f"> {summary}")

    # Steps accordion
    for i, step in enumerate(steps, start=1):
        head = f"{t(lang, 'Step', 'الخطوة')} {i}: {step.get('title','')}"
        with st.expander(head, expanded=(i == 1)):
            if step.get("goal"):
                st.markdown(f"**{t(lang,'Goal','الهدف')}:** {step['goal']}")
            if step.get("talk_track"):
                st.markdown(f"**{t(lang,'Talk Track','نص الحديث')}:** {step['talk_track']}")
            if step.get("evidence"):
                st.markdown(f"**{t(lang,'Evidence','الدليل')}:** {step['evidence']}")
            if step.get("objection"):
                st.markdown(f"**{t(lang,'Objection Handling','التعامل مع الاعتراض')}:** {step['objection']}")
            if step.get("action"):
                st.markdown(f"**{t(lang,'Rep Action','إجراء المندوب')}:** {step['action']}")

    # Closing
    if closing:
        st.markdown("---")
        st.markdown(f"#### {t(lang,'Closing & Next Steps','الختام والخطوات التالية')}")
        if closing.get("cta"):
            st.markdown(f"**{t(lang,'Call to Action','الدعوة للإجراء')}:** {closing['cta']}")
        if closing.get("next_visit_plan"):
            st.markdown(f"**{t(lang,'Next Visit Plan','خطة الزيارة القادمة')}:** {closing['next_visit_plan']}")
        metrics = closing.get("metrics") or []
        if metrics:
            st.markdown(f"**{t(lang,'Metrics to Track','مؤشرات للمتابعة')}:** " + " • ".join(metrics))

def map_len_constraints(resp_len: str):
    if resp_len == "Short":
        return 3, 2, 18
    if resp_len == "Long":
        return 6, 4, 28
    return 4, 3, 22

# --- Language selector ---
language = st.radio("Select Language / اختر اللغة", options=["English", "العربية"])

# --- GSK logo ---
logo_local_path = "images/gsk_logo.png"
logo_fallback_url = "https://www.tungsten-network.com/wp-content/uploads/2020/05/GSK_Logo_Full_Colour_RGB.png"
col1, col2 = st.columns([1,5])
with col1:
    try:
        logo_img = Image.open(logo_local_path)
        st.image(logo_img, width=120)
    except Exception:
        st.image(logo_fallback_url, width=120)
with col2:
    st.title("🧠 AI Sales Call Assistant")

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
race_segments = [
    "R – Reach: Did not start to prescribe yet and Don't believe that vaccination is his responsibility.",
    "A – Acquisition: Prescribe to patient who initiate discussion about the vaccine but Convinced about Shingrix data.",
    "C – Conversion: Proactively initiate discussion with specific patient profile but For other patient profiles he is not prescribing yet.",
    "E – Engagement: Proactively prescribe to different patient profiles"
]
doctor_barriers = [
    "1 - HCP does not consider HZ as risk for the selected patient profile",
    "2 - HCP thinks there is no time to discuss preventive measures with the patients",
    "3 - HCP thinks about cost considerations",
    "4 - HCP is not convinced that HZ Vx is effective in reducing the burden",
    "5 - Accessibility (POVs)"
]
objectives = ["Awareness","Adoption","Retention"]
specialties = ["General Practitioner","Cardiologist","Dermatologist","Endocrinologist","Pulmonologist"]
personas = [
    "Uncommitted Vaccinator – Not engaged, poor knowledge, least likely to prescribe vaccines (26%)",
    "Reluctant Efficiency – Do not see vaccinating 50+ as part of role, least likely to believe in impact (12%)",
    "Patient Influenced – Aware of benefits but prescribes only if patient requests (26%)",
    "Committed Vaccinator – Very positive, motivated, prioritizes vaccination & sets example (36%)"
]
personal_types_experience = ["Most Senior","Junior"]
personal_types_communication = ["Friendly","Masked","Open","Reserved"]
personal_types_mindset = ["Scientific","Emotional","Analytical","Pragmatic"]
gsk_approaches = [
    "Use data-driven evidence",
    "Focus on patient outcomes",
    "Leverage storytelling techniques"
]

# --- Sidebar filters ---
st.sidebar.header("Filters & Options")
if st.sidebar.button("🔄 Reset All Selections"):
    reset_selections()

brand = st.sidebar.selectbox("Select Brand / اختر العلامة التجارية", options=list(gsk_brands.keys()), index=0)
segment = st.sidebar.selectbox("Select RACE Segment / اختر شريحة RACE", race_segments)
barrier = st.sidebar.multiselect("Select Doctor Barrier / اختر حاجز الطبيب", doctor_barriers)
objective = st.sidebar.selectbox("Select Objective / اختر الهدف", objectives)
specialty = st.sidebar.selectbox("Select Doctor Specialty / اختر تخصص الطبيب", specialties)
persona = st.sidebar.selectbox("Select HCP Persona / اختر شخصية الطبيب", personas)

st.sidebar.markdown("### HCP Personal Types / أنماط شخصية الطبيب")
personal_type_exp = st.sidebar.multiselect("Experience Level / مستوى الخبرة", personal_types_experience)
personal_type_comm = st.sidebar.multiselect("Communication Style / أسلوب التواصل", personal_types_communication)
personal_type_mind = st.sidebar.multiselect("Mindset / التوجه الفكري", personal_types_mindset)
personal_type = personal_type_exp + personal_type_comm + personal_type_mind

response_length_options = ["Short","Medium","Long"]
response_tone_options = ["Formal","Casual","Friendly","Persuasive"]
response_length = st.sidebar.selectbox("Select Response Length / اختر طول الرد", response_length_options)
response_tone = st.sidebar.selectbox("Select Response Tone / اختر نبرة الرد", response_tone_options)

max_steps_ui = st.sidebar.slider("Max Steps", 2, 6, st.session_state.filters["max_steps"])
max_bullets_ui = st.sidebar.slider("Max Bullets/Step", 1, 5, st.session_state.filters["max_bullets"])
strict_precision = st.sidebar.checkbox("Strict Precision (very concise)", value=st.session_state.filters["strict_precision"])

st.session_state.filters["max_steps"] = max_steps_ui
st.session_state.filters["max_bullets"] = max_bullets_ui
st.session_state.filters["strict_precision"] = strict_precision

interface_mode = st.sidebar.radio("Interface Mode / اختر واجهة", ["Chatbot","Card Dashboard","Flow Visualization"])

# Chat history options
st.sidebar.subheader("💬 Chat History Options")
if st.sidebar.button("🗑️ Clear Chat / مسح المحادثة"):
    st.session_state.chat_history = []
recall_history = st.sidebar.checkbox("Show Previous History / عرض المحادثات السابقة", value=True)

if st.sidebar.button("📥 Download Chat History"):
    if st.session_state.chat_history:
        history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.chat_history])
        st.download_button("Download TXT", history_text, file_name="chat_history.txt")
    else:
        st.warning("No chat history to download!")

# Brand image
image_path = gsk_brands_images.get(brand)
safe_get_image(image_path, width=200)

# Chat container
chat_container = st.container()
placeholder_text = "Type your message..." if language=="English" else "اكتب رسالتك..."
user_input = st.text_area(placeholder_text, key="user_input", height=80)

# --- Prompt builder ---
def build_prompt() -> str:
    steps_limit_len, bullets_limit_len, max_words = map_len_constraints(response_length)
    steps_limit = min(steps_limit_len, st.session_state.filters["max_steps"])
    bullets_limit = min(st.session_state.filters["max_bullets"],5)

    schema = {
        "title": "string",
        "summary": "string (<= 35 words)",
        "steps": [
            {
                "title": "string",
                "goal": "string",
                "talk_track": f"<= {max_words} words",
                "evidence": f"<= {max_words} words",
                "objection": f"<= {max_words} words",
                "action": f"<= {max_words} words"
            }
        ],
        "closing": {
            "cta": "string",
            "next_visit_plan": "string",
            "metrics": ["string","string"]
        }
    }

    constraints = f"""
- Return ONLY a single JSON object matching the schema below.
- Language: {language} for all strings.
- Sort steps by highest expected impact first.
- Keep every field concise. Each field must be <= {max_words} words.
- Use at most {steps_limit} steps.
- Use at most {bullets_limit} points per field.
- Omit unknown fields.
"""

    compact_style = "ultra concise, telegraphic" if strict_precision or response_length=="Short" else "concise, to-the-point"
    approaches_str = "\n".join(gsk_approaches)
    persona_style = ", ".join(personal_type) if personal_type else "None"

    prompt = f"""
You are an expert GSK sales assistant.

Context:
- RACE Segment: {segment}
- Doctor Barriers: {', '.join(barrier) if barrier else 'None'}
- Objective: {objective}
- Brand: {brand}
- Doctor Specialty: {specialty}
- HCP Persona: {persona}
- HCP Personal Types: {persona_style}
- Response Tone: {response_tone}
- Desired Style: {compact_style}

Approved GSK Sales Approaches:
{approaches_str}

User Input:
{user_input}

{constraints}

JSON Schema:
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""
    return prompt

# --- Send button ---
if st.button("🚀 " + t(language,"Generate Plan","إنشاء الخطة")) and user_input.strip():
    with st.spinner(t(language,"Generating AI response...","جارٍ إنشاء الرد")):
        st.session_state.chat_history.append({"role":"user","content":user_input})
        prompt = build_prompt()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role":"system","content":f"You are a helpful sales assistant that responds in {language}."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2,
            max_tokens=1200
        )
        ai_raw = response.choices[0].message.content
        data = extract_json(ai_raw)
        st.session_state.chat_history.append({
            "role":"ai",
            "content": ai_raw if not data else json.dumps(data, ensure_ascii=False)
        })

        if data:
            st.success(t(language,"Structured plan generated.","تم إنشاء خطة مُنظّمة."))
            render_structured_plan(data, language)
            st.download_button(
                label=t(language,"Download Plan (JSON)","تحميل الخطة (JSON)"),
                data=json.dumps(data, ensure_ascii=False, indent=2),
                file_name="sales_call_plan.json",
                mime="application/json"
            )
        else:
            st.warning(t(language,"Could not parse structured JSON. Showing raw output.","تعذر تحليل JSON المنظّم. عرض المخرجات النصية:"))
            st.markdown(f"<div style='background:#f0f2f6; padding:12px; border-radius:10px'>{ai_raw}</div>", unsafe_allow_html=True)

# --- Render interface ---
with chat_container:
    if interface_mode=="Chatbot":
        st.subheader("💬 Chatbot Interface")
        if recall_history:
            for msg in st.session_state.chat_history:
                role, content = msg["role"], msg["content"]
                if role=="user":
                    st.markdown(f"<div style='text-align:right; background:#d1e7dd; padding:10px; border-radius:12px; margin:10px 0;'>{content}</div>", unsafe_allow_html=True)
                else:
                    data = extract_json(content)
                    if data and "steps" in data:
                        render_structured_plan(data, language)
                    else:
                        st.markdown(f"<div style='text-align:left; background:#f0f2f6; padding:15px; border-radius:12px; margin:10px 0;'>{content}</div>", unsafe_allow_html=True)

    elif interface_mode=="Card Dashboard":
        st.subheader("📊 Card-Based Dashboard")
        last_ai = next((m for m in reversed(st.session_state.chat_history) if m["role"]=="ai"), None)
        data = extract_json(last_ai["content"]) if last_ai else None
        if data:
            st.markdown("#### Overview")
            st.info(data.get("summary",""))
            steps = data.get("steps",[])
            for i, step in enumerate(steps, start=1):
                with st.expander(f"Step {i}: {step.get('title','')}"):
                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown(f"**Goal:** {step.get('goal','')}")
                        st.markdown(f"**Talk Track:** {step.get('talk_track','')}")
                    with cols[1]:
                        st.markdown(f"**Evidence:** {step.get('evidence','')}")
                        st.markdown(f"**Rep Action:** {step.get('action','')}")
                    if step.get("objection"):
                        st.markdown(f"**Objection Handling:** {step['objection']}")
        else:
            st.info("Generate a plan to see cards here.")

    elif interface_mode=="Flow Visualization":
        st.subheader("🔗 HCP Engagement Flow")
        last_ai = next((m for m in reversed(st.session_state.chat_history) if m["role"]=="ai"), None)
        data = extract_json(last_ai["content"]) if last_ai else None
        persona_style = ", ".join(personal_type) if personal_type else "None"
        ai_summary = data.get('summary','Generate a plan to view flow.') if data else 'Generate a plan to view flow.'
        html_content = f"""
        <div style='font-family:sans-serif; background:#f0f2f6; padding:20px; border-radius:10px; line-height:1.5'>
            <h3 style='margin-top:0'>{persona} – {specialty}</h3>
            <p><b>Personal Types:</b> {persona_style}</p>
            <p><b>Barriers:</b> {', '.join(barrier) if barrier else 'None'}</p>
            <p><b>Brand:</b> {brand}</p>
            <p><b>Tone:</b> {response_tone}</p>
            <hr/>
            <p><b>AI Suggestion:</b> {ai_summary}</p>
        </div>
        """
        components.html(html_content, height=320)

# --- Brand leaflet ---
st.markdown(f"[Brand Leaflet - {brand}]({gsk_brands[brand]})")
