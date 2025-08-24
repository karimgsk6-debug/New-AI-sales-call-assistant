import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import groq
from groq import Groq
import json
from typing import Optional, Dict, Any

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
    if not isinstance(s, str) or not s.strip():
        return None
    try:
        return json.loads(s)
    except Exception:
        try:
            start = s.index("{")
            end = s.rindex("}") + 1
            return json.loads(s[start:end])
        except Exception:
            return None

def map_len_constraints(resp_len: str):
    if resp_len == "Short": return 3, 2, 18
    if resp_len == "Long": return 6, 4, 28
    return 4, 3, 22  # Medium

# =========================
# Render structured plan (single language)
# =========================
def render_structured_plan_lang(data: Dict[str, Any], lang: str):
    st.markdown("### " + t(lang, "Sales Call Plan", "خطة الزيارة"))
    
    title = data.get("title", {}).get(lang[:2].upper(), "")
    if title: st.markdown(f"**{title}**")
    
    summary = data.get("summary", {}).get(lang[:2].upper(), "")
    if summary: st.markdown(f"> {summary}")
    
    for i, step in enumerate(data.get("steps", []), start=1):
        step_title = step.get("title", {}).get(lang[:2].upper(), "")
        with st.expander(f"{t(lang,'Step','الخطوة')} {i}: {step_title}", expanded=(i==1)):
            for key in ["goal", "talk_track", "evidence", "objection", "action"]:
                val = step.get(key, {}).get(lang[:2].upper(), "")
                if val: st.markdown(f"**{t(lang,key.capitalize(), key.capitalize())}:** {val}")
    
    closing = data.get("closing", {})
    if closing:
        st.markdown("---")
        st.markdown(f"#### {t(lang,'Closing & Next Steps','الختام والخطوات التالية')}")
        for key in ["cta", "next_visit_plan", "metrics"]:
            val = closing.get(key, {})
            if isinstance(val, list):
                val = " • ".join([v.get(lang[:2].upper(), "") if isinstance(v, dict) else str(v) for v in val])
            elif isinstance(val, dict):
                val = val.get(lang[:2].upper(), "")
            if val: st.markdown(f"**{t(lang,key.replace('_',' ').capitalize(), key.replace('_',' ').capitalize())}:** {val}")

# =========================
# Render generic plan (single language)
# =========================
def render_generic_plan_lang(data: Dict[str, Any], lang: str):
    st.markdown("### " + t(lang,"Generated Sales Call Plan","الخطة المولدة"))
    for section, content in data.items():
        st.markdown(f"#### {section}")
        if isinstance(content, list):
            for item in content:
                val = item.get(lang[:2].upper(), str(item)) if isinstance(item, dict) else str(item)
                st.markdown(f"- {val}")
        elif isinstance(content, dict):
            for k, v in content.items():
                val = v.get(lang[:2].upper(), str(v)) if isinstance(v, dict) else str(v)
                st.markdown(f"**{k}:** {val}")
        else:
            st.markdown(str(content))

# =========================
# App setup
# =========================
st.set_page_config(page_title="AI Sales Call Assistant", layout="wide")

language = st.radio("Select Language / اختر اللغة", ["English", "العربية"], horizontal=True)
st.title(t(language, "🧠 AI Sales Call Assistant", "🧠 مساعد مكالمات المبيعات بالذكاء الاصطناعي"))
st.caption(t(language,
             "Tailor your sales call plan based on persona, barriers, and segment.",
             "خصص خطة الزيارة بناءً على شخصية الطبيب والحواجز والشريحة."))

# =========================
# Data/constants
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
client = Groq(api_key=st.secrets.get("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"))

# =========================
# Session state
# =========================
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "filters" not in st.session_state: st.session_state.filters = {}

def reset_selections():
    st.session_state.filters.clear()

# =========================
# Sidebar
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

max_steps_ui = st.sidebar.slider(t(language,"Max Steps","أقصى عدد للخطوات"), 2, 6, 4)
max_bullets_ui = st.sidebar.slider(t(language,"Max Bullets/Step","أقصى نقاط لكل خطوة"), 1, 5, 3)
strict_precision = st.sidebar.checkbox(t(language,"Strict Precision (very concise)","دقة صارمة (مختصر جدًا)"), True)

interface_mode = st.sidebar.radio(t(language,"Interface Mode","وضع الواجهة"),
                                  [t(language,"Chatbot","الدردشة"),
                                   t(language,"Card Dashboard","لوحة البطاقات"),
                                   t(language,"Flow Visualization","مخطط التدفق")])

# Brand image
st.sidebar.markdown("—")
st.sidebar.markdown(f"**{t(language,'Brand Leaflet','ورقة المنتج')}:** [{brand}]({gsk_brands[brand]})")
safe_get_image(gsk_brands_images.get(brand, ""), width=180)

# =========================
# User input
# =========================
user_input = st.text_area(t(language,"Type your message...","اكتب رسالتك..."), key="user_input", height=80)

# =========================
# Prompt builder
# =========================
def build_prompt() -> str:
    schema = {
        "Probing Questions": ["3–5 open-ended questions with reasoning."],
        "Communication Style": "Detailed guidance with do’s and don’ts.",
        "Objection Handling": {"Barrier Name": "Realistic statement + strong sample response."},
        "Key Messages": ["3–5 messages with 2–3 sentences each."],
        "Closing Strategy": "Detailed closing dialogue."
    }
    constraints = f"""
- Return ONLY a single JSON object following the schema.
- Provide output ONLY in {language}.
- Keep content practical and suitable for a field sales rep.
"""
    persona_style = ", ".join(personal_type) if personal_type else "None"
    approaches_str = "\n".join(gsk_approaches)

    prompt = f"""
You are a pharma sales coach. Create a **very detailed sales call plan** in **{language} only**.

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

User input:
{user_input}

{constraints}

JSON Schema:
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""
    return prompt

# =========================
# Generate plan
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
                                                "You are a helpful sales assistant that replies in the requested language only.",
                                                "أنت مساعد مبيعات مفيد وترد باللغة المطلوبة فقط.")},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1800
        )
        ai_raw = response.choices[0].message.content
        data = extract_json(ai_raw)

        st.session_state.chat_history.append({
            "role": "ai",
            "content": ai_raw if not data else json.dumps(data, ensure_ascii=False)
        })

        if data:
            st.success(t(language,"Structured plan generated.","تم إنشاء خطة مُنظّمة."))
            if "steps" in data or "closing" in data or "summary" in data:
                render_structured_plan_lang(data, language)
            else:
                render_generic_plan_lang(data, language)

            # Download options
            if HAS_DOCX:
                try:
                    doc = Document()
                    doc.add_heading(t(language,"Sales Call Plan","خطة الزيارة"), 0)
                    def write_section(title, content):
                        doc.add_heading(str(title), level=1)
                        if isinstance(content, list):
                            for item in content: doc.add_paragraph(str(item))
                        elif isinstance(content, dict):
                            for k, v in content.items(): doc.add_paragraph(f"{k}: {v}")
                        else:
                            doc.add_paragraph(str(content))
                    if isinstance(data, dict):
                        for k, v in data.items(): write_section(k, v)
                    else: doc.add_paragraph(str(data))
                    buf = BytesIO()
                    doc.save(buf)
                    buf.seek(0)
                    st.download_button(
                        t(language,"📥 Download Plan (Word)","📥 تنزيل الخطة (وورد)"),
                        buf,
                        file_name="sales_call_plan.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception:
                    st.download_button(
                        t(language,"📥 Download Plan (JSON)","📥 تنزيل الخطة (JSON)"),
                        json.dumps(data, ensure_ascii=False, indent=2),
                        file_name="sales_call_plan.json",
                        mime="application/json"
                    )
            else:
                st.download_button(
                    t(language,"📥 Download Plan (JSON)","📥 تنزيل الخطة (JSON)"),
                    json.dumps(data, ensure_ascii=False, indent=2),
                    file_name="sales_call_plan.json",
                    mime="application/json"
                )
        else:
            st.warning(t(language,"Could not parse structured JSON. Showing raw output:",
                         "تعذّر تحليل JSON المنظّم. سيتم عرض المخرجات النصية:"))
            st.markdown(f"<div style='background:#f0f2f6; padding:12px; border-radius:10px'>{ai_raw}</div>", unsafe_allow_html=True)

# =========================
# Chat history
# =========================
if st.session_state.chat_history:
    st.subheader(t(language,"💬 Chat History","💬 سجلّ الدردشة"))
    for msg in st.session_state.chat_history:
        role = t(language, "🧑‍💼 You", "🧑‍💼 أنت") if msg["role"] == "user" else t(language, "🤖 Assistant", "🤖 المساعد")
        st.markdown(f"**{role}:** {msg['content']}")
