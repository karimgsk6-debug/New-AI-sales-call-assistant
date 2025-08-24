import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import groq
from groq import Groq
import streamlit.components.v1 as components
import json, re
from typing import Optional, Dict, Any, List

# --- Initialize Groq client ---
client = Groq(api_key="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")  # <-- add your key

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
    # Try direct parse
    try:
        return json.loads(s)
    except Exception:
        pass
    # Try to extract largest JSON object
    match = re.search(r"\{(?:[^{}]|(?R))*\}", s, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
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
    # Tune compactness
    if resp_len == "Short":
        return 3, 2, 18  # steps, bullets, max words/field
    if resp_len == "Long":
        return 6, 4, 28
    return 4, 3, 22  # Medium

# --- Language selector ---
language = st.radio("Select Language / اختر اللغة", options=["English", "العربية"])

# --- GSK logo ---
logo_local_path = "images/gsk_logo.png"
logo_fallback_url = "https://www.tungsten-network.com/wp-content/uploads/2020/05/GSK_Logo_Full_Colour_RGB.png"
col1, col2 = st.columns([1, 5])
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
objectives = ["Awareness", "Adoption", "Retention"]
specialties = ["General Practitioner", "Cardiologist", "Dermatologist", "Endocrinologist", "Pulmonologist"]
personas = [
    "Uncommitted Vaccinator – Not engaged, poor knowledge, least likely to prescribe vaccines (26%)",
    "Reluctant Efficiency – Do not see vaccinating 50+ as part of role, least likely to believe in impact (12%)",
    "Patient Influenced – Aware of benefits but prescribes only if patient requests (26%)",
    "Committed Vaccinator – Very positive, motivated, prioritizes vaccination & sets example (36%)"
]
personal_types_experience = ["Most Senior", "Junior"]
personal_types_communication = ["Friendly", "Masked", "Open", "Reserved"]
personal_types_mindset = ["Scientific", "Emotional", "Analytical", "Pragmatic"]
gsk_approaches = [
    "Use data-driven evidence",
    "Focus on patient outcomes",
    "Leverage storytelling techniques",
]

# --- Sidebar Filters ---
st.sidebar.header("Filters & Options")
if st.sidebar.button("🔄 Reset All Selections"):
    reset_selections()

brand = st.sidebar.selectbox("Select Brand / اختر العلامة التجارية", options=list(gsk_brands.keys()), index=0)
segment = st.sidebar.selectbox("Select RACE Segment / اختر شريحة RACE", race_segments)
barrier = st.sidebar.multiselect("Select Doctor Barrier / اختر حاجز الطبيب", options=doctor_barriers)
objective = st.sidebar.selectbox("Select Objective / اختر الهدف", objectives)
specialty = st.sidebar.selectbox("Select Doctor Specialty / اختر تخصص الطبيب", specialties)
persona = st.sidebar.selectbox("Select HCP Persona / اختر شخصية الطبيب", personas)

st.sidebar.markdown("### HCP Personal Types / أنماط شخصية الطبيب")
personal_type_exp = st.sidebar.multiselect("Experience Level / مستوى الخبرة", options=personal_types_experience)
personal_type_comm = st.sidebar.multiselect("Communication Style / أسلوب التواصل", options=personal_types_communication)
personal_type_mind = st.sidebar.multiselect("Mindset / التوجه الفكري", options=personal_types_mindset)
personal_type = personal_type_exp + personal_type_comm + personal_type_mind

response_length_options = ["Short", "Medium", "Long"]
response_tone_options = ["Formal", "Casual", "Friendly", "Persuasive"]
response_length = st.sidebar.selectbox("Select Response Length / اختر طول الرد", response_length_options)
response_tone = st.sidebar.selectbox("Select Response Tone / اختر نبرة الرد", response_tone_options)

# Precision controls
max_steps_ui = st.sidebar.slider("Max Steps", 2, 6, st.session_state.filters["max_steps"])
max_bullets_ui = st.sidebar.slider("Max Bullets/Step", 1, 5, st.session_state.filters["max_bullets"])
strict_precision = st.sidebar.checkbox("Strict Precision (very concise)", value=st.session_state.filters["strict_precision"])

st.session_state.filters["max_steps"] = max_steps_ui
st.session_state.filters["max_bullets"] = max_bullets_ui
st.session_state.filters["strict_precision"] = strict_precision

interface_mode = st.sidebar.radio("Interface Mode / اختر واجهة", ["Chatbot", "Card Dashboard", "Flow Visualization"])

# --- Chat history options ---
st.sidebar.subheader("💬 Chat History Options")
if st.sidebar.button("🗑️ Clear Chat / مسح المحادثة"):
    st.session_state.chat_history = []
recall_history = st.sidebar.checkbox("Show Previous History / عرض المحادثات السابقة", value=True)

# --- Download chat history ---
if st.sidebar.button("📥 Download Chat History"):
    if st.session_state.chat_history:
        history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.chat_history])
        st.download_button("Download TXT", history_text, file_name="chat_history.txt")
    else:
        st.warning("No chat history to download!")

# --- Load brand image safely ---
image_path = gsk_brands_images.get(brand)
safe_get_image(image_path, width=200)

# --- Chat container ---
chat_container = st.container()
placeholder_text = "Type your message..." if language == "English" else "اكتب رسالتك..."
user_input = st.text_area(placeholder_text, key="user_input", height=80)

# --- Prompt builder (strict JSON, sorted, step-by-step) ---
def build_prompt() -> str:
    steps_limit_len, bullets_limit_len, max_words = map_len_constraints(response_length)
    steps_limit = min(steps_limit_len, st.session_state.filters["max_steps"])
    bullets_limit = min(st.session_state.filters["max_bullets"], 5)

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
            "metrics": ["string", "string"]
        }
    }

    constraints = f"""
- Return ONLY a single JSON object matching the schema below. No prose, no markdown, no backticks.
- Language: {language} for ALL strings.
- Sort steps by highest expected impact first.
- Keep EVERY field concise. Each field must be <= {max_words} words.
- Use at most {steps_limit} steps.
- Use at most {bullets_limit} concrete points within each field (implicit by brevity).
- If information is unknown, omit the field.
- Do NOT include citations, links, or markdown.
"""

    compact_style = "ultra concise, telegraphic" if strict_precision or response_length == "Short" else "concise, to-the-point"

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
- HCP Persona (adoption-based): {persona}
- HCP Personal Types (style-based): {persona_style}
- Response Tone: {response_tone}
- Desired style: {compact_style}

Approved GSK Sales Approaches to reflect:
{approaches_str}

User input (agent question or visit context):
{user_input}

{constraints}

JSON Schema (descriptive, not literal types):
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""
    return prompt

# --- Send button ---
if st.button("🚀 " + t(language, "Generate Plan", "إنشاء الخطة")) and user_input.strip():
    with st.spinner(t(language, "Generating AI response...", "جارٍ إنشاء الرد")):
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        prompt = build_prompt()

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": f"You are a helpful sales assistant that responds in {language}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # lower temp for precision
            max_tokens=1200
        )
        ai_raw = response.choices[0].message.content
        data = extract_json(ai_raw)

        # Save both raw and parsed for transparency
        st.session_state.chat_history.append({
            "role": "ai",
            "content": ai_raw if not data else json.dumps(data, ensure_ascii=False)
        })

        # Display immediately below
        if data:
            st.success(t(language, "Structured plan generated.", "تم إنشاء خطة مُنظّمة."))
            render_structured_plan(data, language)
            # Offer download of JSON
            st.download_button(
                label=t(language, "Download Plan (JSON)", "تحميل الخطة (JSON)"),
                data=json.dumps(data, ensure_ascii=False, indent=2),
                file_name="sales_call_plan.json",
                mime="application/json"
            )
        else:
            st.warning(t(language, "Could not parse structured JSON. Showing raw output:", "تعذر تحليل JSON المنظّم. عرض المخرجات النصية:"))
            st.markdown(f"<div style='background:#f0f2f6; padding:12px; border-radius:10px'>{ai_raw}</div>", unsafe_allow_html=True)

# --- Display chat history / interface ---
with chat_container:
    if interface_mode == "Chatbot":
        st.subheader("💬 " + t(language, "Chatbot Interface", "واجهة الدردشة"))
        if recall_history:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(
                        f"<div style='text-align:right; background:#d1e7dd; padding:10px; border-radius:12px; margin:10px 0;'>{msg['content']}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    # Try rendering as structured if it's valid JSON
                    data = extract_json(msg["content"])
                    if data and isinstance(data, dict) and "steps" in data:
                        with st.container():
                            render_structured_plan(data, language)
                    else:
                        st.markdown(
                            f"<div style='text-align:left; background:#f0f2f6; padding:15px; border-radius:12px; margin:10px 0; box-shadow:2px 2px 5px rgba(0,0,0,0.1);'>{msg['content']}</div>",
                            unsafe_allow_html=True
                        )

    elif interface_mode == "Card Dashboard":
        st.subheader("📊 " + t(language, "Card-Based Dashboard", "لوحة البطاقات"))
        # If last AI message is structured, show summary cards
        last_ai = next((m for m in reversed(st.session_state.chat_history) if m["role"] == "ai"), None)
        data = extract_json(last_ai["content"]) if last_ai else None
        if data:
            st.markdown("#### " + t(language, "Overview", "نظرة عامة"))
            st.info(data.get("summary", ""))
            steps = data.get("steps", [])
            for i, step in enumerate(steps, start=1):
                with st.expander(f"{t(language,'Step','الخطوة')} {i}: {step.get('title','')}"):
                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown(f"**{t(language,'Goal','الهدف')}:** {step.get('goal','')}")
                        st.markdown(f"**{t(language,'Talk Track','نص الحديث')}:** {step.get('talk_track','')}")
                    with cols[1]:
                        st.markdown(f"**{t(language,'Evidence','الدليل')}:** {step.get('evidence','')}")
                        st.markdown(f"**{t(language,'Rep Action','إجراء المندوب')}:** {step.get('action','')}")
                    if step.get("objection"):
                        st.markdown(f"**{t(language,'Objection Handling','التعامل مع الاعتراض')}:** {step['objection']}")
        else:
            st.info(t(language, "Generate a plan to see cards here.", "أنشئ خطة لعرض البطاقات هنا."))

    elif interface_mode == "Flow Visualization":
        st.subheader("🔗 " + t(language, "HCP Engagement Flow", "مخطط تفاعل الطبيب"))
        last_ai = next((m for m in reversed(st.session_state.chat_history) if m["role"] == "ai"), None)
        data = extract_json(last_ai["content"]) if last_ai else None
        persona_style = ", ".join(personal_type) if personal_type else "None"
        html_content = f"""
        <div style='font-family:sans-serif; background:#f0f2f6; padding:20px; border-radius:10px; line-height:1.5'>
            <h3 style='margin-top:0'>{persona} – {specialty}</h3>
            <p><b>{t(language,'Personal Types','الأنماط الشخصية')}:</b> {persona_style}</p>
            <p><b>{t(language,'Barriers','الحواجز')}:</b> {', '.join(barrier) if barrier else 'None'}</p>
            <p><b>{t(language,'Brand','العلامة التجارية')}:</b> {brand}</p>
            <p><b>{t(language,'Tone','النبرة')}:</b> {response_tone}</p>
            <hr/>
            <p><b>{t(language,'AI Suggestion','اقتراح الذكاء الاصطناعي')}:</b> { (data.get('summary','') if data else t(language,'Generate a plan to view flow.','أنشئ خطة لعرض المخطط.')) }</p>
        </div>
        """
        components.html(html_content, height=320)

# --- Brand leaflet ---
st.markdown(f"[{t(language,'Brand Leaflet','ورقة المنتج')} - {brand}]({gsk_brands[brand]})")
