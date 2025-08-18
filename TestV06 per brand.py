import streamlit as st
import os
from groq import Groq

# Initialize Groq client with your API key
client = Groq(api_key="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",)

# Define GSK brands with links to public PILs
gsk_brands = {
    "Shingrix": "https://www.medicines.org.uk/emc/product/12555/pil",
    "Augmentin": "https://www.medicines.org.uk/emc/product/1112/pil",
    "Seretide": "https://www.medicines.org.uk/emc/product/76/pil",
}

# Brand images (replace URLs with official GSK images or local files)
brand_images = {
    "Shingrix": "https://www.gsk.com/media/11255/shingrix.png",
    "Augmentin": "https://www.gsk.com/media/1112/augmentin.png",
    "Seretide": "https://www.gsk.com/media/76/seretide.png"
}

# Approved GSK Sales Approaches
gsk_approaches = [
    "Awareness & Disease Education",
    "Product Efficacy & Clinical Evidence",
    "Safety Profile & Tolerability",
    "Dosing & Administration",
    "Patient Support & Adherence",
    "Objection Handling"
]

# Language selection
language = st.selectbox("🌐 Select Language / اختر اللغة:", ["English", "العربية"])

# Translations dictionary
translations = {
    "English": {
        "title": "🧠 AI Sales Call Assistant",
        "description": "Prepare for HCP visits with AI-powered suggestions.",
        "select_segment": "Select Doctor Segment:",
        "select_behavior": "Select Doctor Behavior:",
        "select_objective": "Select Visit Objective:",
        "select_brand": "Select GSK Brand:",
        "generate": "Generate AI Suggestions",
        "loading": "Generating recommendations...",
        "result_title": "🤖 AI Recommendations",
        "leaflet": "📄 Patient Information Leaflet",
        "approved_approaches": "✅ Approved GSK Sales Approaches",
        "segments": ["Evidence-Seeker", "Skeptic", "Time-Pressured", "Early Adopter", "Traditionalist"],
        "behaviors": ["Scientific", "Skeptical", "Passive", "Emotional", "Argumentative"],
        "objectives": ["Awareness", "Objection Handling", "Follow-up", "New Launch", "Reminder"],
        "system_prompt": "You are an expert pharma sales assistant AI.",
        "user_prompt": """
You are an expert pharma sales assistant AI.

Based on:
- Segment: {segment}
- Behavior: {behavior}
- Visit Objective: {objective}
- Brand: {brand}

Use the official GSK Selling Approaches as your framework:
{approaches}

Brand-specific guidance:
- If the brand is **Shingrix**, focus on:
  * Herpes Zoster risk and disease burden
  * Vaccine efficacy and immunization schedules
  * Patient eligibility and safety profile
  * Strategies to increase patient adherence
- If the brand is **Augmentin**, focus on:
  * Antibiotic spectrum and efficacy
  * Clinical indications and treatment guidelines
  * Safety and tolerability
  * Patient adherence and counseling
- If the brand is **Seretide**, focus on:
  * Asthma/COPD management
  * Inhaler technique and adherence
  * Clinical evidence and safety profile
  * Individual patient optimization

Your tasks:
1. Suggest **three probing questions** aligned with the most relevant GSK selling approach.
2. Recommend a **communication style** that matches the doctor’s profile and the chosen approach.
3. Select **ONE selling approach only** from the approved list above and **bold it in your response**.
4. Adapt your suggestions so they remain fully compliant with the approved GSK selling approaches.

Be specific, concise, and practical.
"""
    },
    "العربية": {
        "title": "🧠 مساعد الزيارات الطبية بالذكاء الاصطناعي",
        "description": "استعد لزيارة الأطباء باقتراحات مدعومة بالذكاء الاصطناعي.",
        "select_segment": "اختر نوع الطبيب:",
        "select_behavior": "اختر سلوك الطبيب:",
        "select_objective": "اختر هدف الزيارة:",
        "select_brand": "اختر منتج من GSK:",
        "generate": "احصل على الاقتراحات",
        "loading": "جاري توليد الاقتراحات...",
        "result_title": "🤖 اقتراحات الذكاء الاصطناعي",
        "leaflet": "📄 النشرة الدوائية للمريض",
        "approved_approaches": "✅ أساليب البيع المعتمدة من GSK",
        "segments": ["باحث عن الأدلة", "مشكك", "مضغوط بالوقت", "مبكر التبني", "تقليدي"],
        "behaviors": ["علمي", "مشكك", "سلبي", "عاطفي", "مجادل"],
        "objectives": ["زيادة الوعي", "التعامل مع الاعتراضات", "متابعة", "إطلاق جديد", "تذكير"],
        "system_prompt": "أنت مساعد خبير في مبيعات الأدوية مدعوم بالذكاء الاصطناعي.",
        "user_prompt": """
أنت مساعد خبير في مبيعات الأدوية مدعوم بالذكاء الاصطناعي.

بناءً على:
- نوع الطبيب: {segment}
- سلوك الطبيب: {behavior}
- هدف الزيارة: {objective}
- المنتج: {brand}

استخدم أساليب البيع المعتمدة من GSK كإطار عمل:
{approaches}

إرشادات مخصصة حسب المنتج:
- إذا كان المنتج هو **Shingrix**، ركز على:
  * خطر مرض القوباء المنطقية وعبء المرض
  * فعالية اللقاح وجداول التطعيم
  * أهلية المرضى والملف الأمني
  * استراتيجيات لتعزيز التزام المرضى
- إذا كان المنتج هو **Augmentin**، ركز على:
  * نطاق المضاد الحيوي وفعاليته
  * المؤشرات السريرية وإرشادات العلاج
  * السلامة والتحمل
  * التزام المرضى والتثقيف
- إذا كان المنتج هو **Seretide**، ركز على:
  * إدارة الربو وCOPD
  * طريقة استخدام الجهاز واتباع العلاج
  * الأدلة السريرية والملف الأمني
  * تحسين العلاج حسب حالة المريض

المطلوب:
1. اقترح **ثلاثة أسئلة استكشافية** مرتبطة بأسلوب البيع الأنسب.
2. أوصِ بـ **أسلوب التواصل** الأنسب الذي يتماشى مع ملف الطبيب والأسلوب المختار.
3. اختر **أسلوب بيع واحد فقط** من القائمة أعلاه وضعه بالخط العريض في ردك.
4. عدّل اقتراحاتك لتبقى ملتزمة تمامًا بالأساليب المعتمدة من GSK.

الرجاء الرد باللغة العربية فقط، وكن محددًا وعمليًا.
"""
    }
}

# Load language dictionary
t = translations[language]

# UI
st.title(t["title"])
st.markdown(t["description"])

segment = st.selectbox(t["select_segment"], t["segments"])
behavior = st.selectbox(t["select_behavior"], t["behaviors"])
objective = st.selectbox(t["select_objective"], t["objectives"])
brand = st.selectbox(t["select_brand"], list(gsk_brands.keys()))

# Display brand image
if brand in brand_images:
    st.image(brand_images[brand], width=150)

# Show approved selling approaches
st.subheader(t["approved_approaches"])
for a in gsk_approaches:
    st.write(f"- {a}")

# Generate AI suggestions
if st.button(t["generate"]):
    with st.spinner(t["loading"]):
        approaches_str = "\n".join(gsk_approaches)
        prompt = t["user_prompt"].format(
            segment=segment,
            behavior=behavior,
            objective=objective,
            brand=brand,
            approaches=approaches_str
        )

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": t["system_prompt"]},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        ai_output = response.choices[0].message.content
        st.subheader(t["result_title"])
        st.markdown(ai_output)

        # Add PIL link
        st.markdown(f"[{t['leaflet']} - {brand}]({gsk_brands[brand]})")
