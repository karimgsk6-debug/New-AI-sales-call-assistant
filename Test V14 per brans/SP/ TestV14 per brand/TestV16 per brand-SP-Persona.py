import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import groq
from groq import Groq
import streamlit.components.v1 as components  # (kept in case you use it later)
import json
from typing import Optional, Dict, Any, List

# =========================
# Safe import for Word export
# =========================
try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# =========================
# Helpers
# =========================
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
    """
    Safely extract and parse JSON from a string.
    1) Try direct parse
    2) Fallback to slice between first '{' and last '}'
    """
    if not isinstance(s, str) or not s.strip():
        return None
    # try direct
    try:
        return json.loads(s)
    except Exception:
        pass
    # fallback slice
    try:
        start = s.index("{")
        end = s.rindex("}") + 1
        return json.loads(s[start:end])
    except Exception:
        return None

def map_len_constraints(resp_len: str):
    if resp_len == "Short":
        return 3, 2, 18
    if resp_len == "Long":
        return 6, 4, 28
    return 4, 3, 22  # Medium

def render_structured_plan(data: Dict[str, Any], lang: str):
    """Renders a structured 'steps' style plan (if present)."""
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
            for key, label_en, label_ar in [
                ("goal", "Goal", "الهدف"),
                ("talk_track", "Talk Track", "نص الحديث"),
                ("evidence", "Evidence", "الدليل"),
                ("objection", "Objection Handling", "التعامل مع الاعتراض"),
                ("action", "Rep Action", "إجراء المندوب"),
            ]:
                if step.get(key):
                    st.markdown(f"**{t(lang,label_en,label_ar)}:** {step[key]}")

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

def render_generic_bilingual(data: Dict[str, Any], lang: str):
    """Renders generic, dictionary-based bilingual sections (Probing Questions, Objections, etc.)."""
    st.markdown("### " + t(lang, "Generated Sales Call Plan (EN + AR)", "الخطة المولدة (إنجليزي + عربي)"))
    for section, content in data.items():
        st.markdown(f"#### {section}")
        if isinstance(content, list):
            for item in content:
                st.markdown(f"- {item}")
        elif isinstance(content, dict):
            for k, v in content.items():
                st.markdown(f"**{k}:** {v}")
        else:
            st.markdown(str(content))

# =========================
# App Setup
# =========================
st.set_page_config(page_title="AI Sales Call Assistant", layout="wide")

# Language selector
language = st.radio("Select Language / اختر اللغة", options=["English", "العربية"], horizontal=True)

st.title(t(language, "🧠 AI Sales Call Assistant", "🧠 مساعد مكالمات المبيعات بالذكاء الاصطناعي"))
st.caption(t(language,
             "Tailor your sales call plan based on persona, barriers, and segment.",
             "خصص خطة الزيارة بناءً على شخصية الطبيب والحواجز والشريحة."))

# =========================
# Data / constants
# =========================
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
race_segments = ["R – Reach", "A – Acquisition", "C – Conversion", "E – Engagement"]
doctor_barriers = [
    t(language, "1 - HCP does not consider HZ a risk", "1 - لا يعتبر الطبيب القوباء المنطقية خطراً"),
    t(language, "2 - No time", "2 - لا يوجد وقت"),
    t(language, "3 - Cost concern", "3 - مشكلة التكلفة"),
    t(language, "4 - Not convinced", "4 - غير مقتنع بالفعالية"),
    t(language, "5 - Accessibility", "5 - صعوبة الوصول (POVs)"),
]
objectives = [t(language,"Awareness","التوعية"), t(language,"Adoption","التبني"), t(language,"Retention","الاستمرارية")]
specialties = [
    t(language,"General Practitioner","طبيب أسرة"),
    t(language,"Cardiologist","طبيب قلب"),
    t(language,"Dermatologist","طبيب جلدية"),
    t(language,"Endocrinologist","طبيب غدد"),
    t(language,"Pulmonologist","طبيب رئة"),
]
personas = [
    t(language,"Uncommitted Vaccinator","غير ملتزم بالتطعيم"),
    t(language,"Reluctant Efficiency","كفء متردد"),
    t(language,"Patient Influenced","متأثر بطلبات المريض"),
    t(language,"Committed Vaccinator","ملتزم بالتطعيم"),
]
personal_types_experience = [t(language,"Most Senior","الأكثر خبرة"), t(language,"Junior","مبتدئ")]
personal_types_communication = [t(language,"Friendly","ودود"), t(language,"Masked","متحفظ"), t(language,"Open","منفتح"), t(language,"Reserved","رزين")]
personal_types_mindset = [t(language,"Scientific","علمي"), t(language,"Emotional","عاطفي"), t(language,"Analytical","تحليلي"), t(language,"Pragmatic","عملي")]
gsk_approaches = [
    t(language,"Use data-driven evidence","استخدم الأدلة المبنية على البيانات"),
    t(language,"Focus on patient outcomes","ركز على نتائج المريض"),
    t(language,"Leverage storytelling techniques","استخدم أساليب السرد القصصي"),
]

# =========================
# Initialize Groq client
# =========================
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "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"))  # put your key in Streamlit secrets

# =========================
# Session state
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "filters" not in st.session_state:
    st.session_state.filters = {
        "brand": None, "segment": None, "barrier": [],
        "objective": None, "specialty": None, "persona": None,
        "personal_type_exp": [], "personal_type_comm": [], "personal_type_mind": [],
        "response_length": "Medium", "response_tone": "Formal", "interface_mode": "Chatbot",
        "max_steps": 4, "max_bullets": 3, "strict_precision": True,
    }

def reset_selections():
    st.session_state.filters.update({
        "brand": None, "segment": None, "barrier": [],
        "objective": None, "specialty": None, "persona": None,
        "personal_type_exp": [], "personal_type_comm": [], "personal_type_mind": [],
        "response_length": "Medium", "response_tone": "Formal", "interface_mode": "Chatbot",
        "max_steps": 4, "max_bullets": 3, "strict_precision": True,
    })

# =========================
# Sidebar (bilingual)
# =========================
st.sidebar.header(t(language,"Filters & Options","المرشحات والخيارات"))
if st.sidebar.button("🔄 " + t(language, "Reset All Selections", "إعادة ضبط جميع الاختيارات")):
    reset_selections()

brand = st.sidebar.selectbox(t(language,"Brand","العلامة التجارية"), list(gsk_brands.keys()))
segment = st.sidebar.selectbox(t(language,"RACE Segment","شريحة RACE"), race_segments)
barrier = st.sidebar.multiselect(t(language,"Doctor Barrier","حواجز الطبيب"), doctor_barriers)
objective = st.sidebar.selectbox(t(language,"Objective","الهدف"), objectives)
specialty = st.sidebar.selectbox(t(language,"Specialty","التخصص"), specialties)
persona = st.sidebar.selectbox(t(language,"HCP Persona","شخصية الطبيب"), personas)
personal_type_exp = st.sidebar.multiselect(t(language,"Experience Level","مستوى الخبرة"), personal_types_experience)
personal_type_comm = st.sidebar.multiselect(t(language,"Communication Style","أسلوب التواصل"), personal_types_communication)
personal_type_mind = st.sidebar.multiselect(t(language,"Mindset","العقلية"), personal_types_mindset)
personal_type = personal_type_exp + personal_type_comm + personal_type_mind

response_length_options = ["Short","Medium","Long"]
response_tone_options = ["Formal","Casual","Friendly","Persuasive"]
response_length = st.sidebar.selectbox(t(language,"Response Length","طول الرد"), response_length_options)
response_tone = st.sidebar.selectbox(t(language,"Response Tone","نبرة الرد"), response_tone_options)

max_steps_ui = st.sidebar.slider(t(language,"Max Steps","أقصى عدد للخطوات"), 2, 6, st.session_state.filters["max_steps"])
max_bullets_ui = st.sidebar.slider(t(language,"Max Bullets/Step","أقصى نقاط لكل خطوة"), 1, 5, st.session_state.filters["max_bullets"])
strict_precision = st.sidebar.checkbox(t(language,"Strict Precision (very concise)","دقة صارمة (مختصر جدًا)"),
                                       value=st.session_state.filters["strict_precision"])
st.session_state.filters.update({"max_steps": max_steps_ui,"max_bullets": max_bullets_ui,"strict_precision": strict_precision})

interface_mode = st.sidebar.radio(t(language,"Interface Mode","وضع الواجهة"),
                                  [t(language,"Chatbot","الدردشة"),
                                   t(language,"Card Dashboard","لوحة البطاقات"),
                                   t(language,"Flow Visualization","مخطط التدفق")])

# Brand image
st.sidebar.markdown("—")
st.sidebar.markdown(f"**{t(language,'Brand Leaflet','ورقة المنتج')}:** [{brand}]({gsk_brands[brand]})")
safe_get_image(gsk_brands_images.get(brand, ""), width=180)

# =========================
# Main input
# =========================
user_input = st.text_area(t(language,"Type your message...","اكتب رسالتك..."), key="user_input", height=80)

# =========================
# Prompt builder (bilingual, detailed examples)
# =========================
def build_prompt() -> str:
    steps_limit_len, bullets_limit_len, max_words = map_len_constraints(response_length)
    steps_limit = min(steps_limit_len, st.session_state.filters["max_steps"])
    bullets_limit = min(st.session_state.filters["max_bullets"], 5)

    schema = {
        "Probing Questions": [
            "3–5 open-ended questions, each in EN + AR, with a short note on why it is effective."
        ],
        "Communication Style": "Detailed guidance with at least 2 do’s and 2 don’ts; include EN + AR phrasing tips.",
        "Objection Handling": {
            "Barrier Name": "Realistic doctor statement (EN + AR) + strong sample response (EN + AR) with supporting rationale."
        },
        "Key Messages": [
            "3–5 messages; each elaborated in 2–3 sentences with EN + AR examples."
        ],
        "Closing Strategy": "Detailed closing; EN + AR dialogue for commitment and next steps."
    }

    constraints = f"""
- Return ONLY a single JSON object following the schema below (no markdown, no backticks).
- Provide **bilingual output** (English + Arabic) for questions, objections, key messages, and closing dialogue.
- Be **descriptive and practical** with concrete examples suitable for a field sales rep.
- Sort/organize content logically; keep each individual item concise but informative.
- If unknown, omit the field/key entirely.
"""

    persona_style = ", ".join(personal_type) if personal_type else "None"
    approaches_str = "\n".join(gsk_approaches)

    prompt = f"""
You are a pharma sales coach. Create a **very detailed and descriptive bilingual (English + Arabic) sales call plan**.

Context:
- Brand: {brand}
- RACE Segment: {segment}
- Doctor Barriers: {', '.join(barrier) if barrier else 'None'}
- Objective: {objective}
- Specialty: {specialty}
- HCP Persona: {persona}
- HCP Personal Types: {persona_style}
- Response Tone: {response_tone}

Approved GSK Sales Approaches to reflect:
{approaches_str}

Agent/User input:
{user_input}

{constraints}

JSON Schema (descriptive):
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""
    return prompt

# =========================
# Generate Plan
# =========================
go_label = "🚀 " + t(language,"Generate Plan","إنشاء الخطة")
if st.button(go_label) and user_input.strip():
    with st.spinner(t(language,"Generating AI response...","جارٍ إنشاء الرد...")):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        prompt = build_prompt()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": t(language,
                                                "You are a helpful sales assistant that replies in English and Arabic where requested.",
                                                "أنت مساعد مبيعات مفيد وترد باللغتين الإنجليزية والعربية عند الطلب.")},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1800
        )
        ai_raw = response.choices[0].message.content
        data = extract_json(ai_raw)

        # save to history (raw for debugging / parsed for reuse)
        st.session_state.chat_history.append({
            "role": "ai",
            "content": ai_raw if not data else json.dumps(data, ensure_ascii=False)
        })

        # render
        if data:
            st.success(t(language,"Structured plan generated.","تم إنشاء خطة مُنظّمة."))
            # Try to detect if it's "steps" style or generic bilingual structure
            if "steps" in data or "closing" in data or "summary" in data:
                render_structured_plan(data, language)
            else:
                render_generic_bilingual(data, language)

            # Download options
            if HAS_DOCX:
                try:
                    doc = Document()
                    doc.add_heading(t(language,"Sales Call Plan (EN + AR)","خطة الزيارة (إنجليزي + عربي)"), 0)

                    # write content smartly
                    def write_section(title, content):
                        doc.add_heading(str(title), level=1)
                        if isinstance(content, list):
                            for item in content:
                                doc.add_paragraph(f"- {item}")
                        elif isinstance(content, dict):
                            for k, v in content.items():
                                doc.add_paragraph(f"{k}: {v}")
                        else:
                            doc.add_paragraph(str(content))

                    if isinstance(data, dict):
                        for k, v in data.items():
                            write_section(k, v)
                    else:
                        doc.add_paragraph(str(data))

                    buf = BytesIO()
                    doc.save(buf)
                    buf.seek(0)
                    st.download_button(
                        t(language,"📥 Download Plan (Word)","📥 تنزيل الخطة (وورد)"),
                        buf,
                        file_name="sales_call_plan_bilingual.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception:
                    st.warning(t(language,"Word export failed. Offering JSON instead.","فشل تصدير ملف وورد. سيتم توفير JSON بدلًا منه."))
                    st.download_button(
                        t(language,"📥 Download Plan (JSON)","📥 تنزيل الخطة (JSON)"),
                        json.dumps(data, ensure_ascii=False, indent=2),
                        file_name="sales_call_plan_bilingual.json",
                        mime="application/json"
                    )
            else:
                st.warning(t(language,"python-docx is not installed. Falling back to JSON download.",
                             "حزمة python-docx غير مثبتة. سيتم توفير التنزيل بصيغة JSON."))
                st.download_button(
                    t(language,"📥 Download Plan (JSON)","📥 تنزيل الخطة (JSON)"),
                    json.dumps(data, ensure_ascii=False, indent=2),
                    file_name="sales_call_plan_bilingual.json",
                    mime="application/json"
                )
        else:
            st.warning(t(language,"Could not parse structured JSON. Showing raw output:",
                         "تعذّر تحليل JSON المنظّم. سيتم عرض المخرجات النصية:"))
            st.markdown(f"<div style='background:#f0f2f6; padding:12px; border-radius:10px'>{ai_raw}</div>", unsafe_allow_html=True)

# =========================
# Chat history (bilingual label)
# =========================
if st.session_state.chat_history:
    st.subheader(t(language,"💬 Chat History","💬 سجلّ الدردشة"))
    for msg in st.session_state.chat_history:
        role = t(language, "🧑‍💼 You", "🧑‍💼 أنت") if msg["role"] == "user" else t(language, "🤖 Assistant", "🤖 المساعد")
        st.markdown(f"**{role}:** {msg['content']}")
