import streamlit as st
import os
from groq import Groq

# Load API key (best from secrets or env variable)
client = Groq(api_key="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")  # Add your API key here

# Define GSK brands with links to public PILs
gsk_brands = {
    "Augmentin": "https://www.medicines.org.uk/emc/product/1112/pil",
    "Ventolin": "https://www.medicines.org.uk/emc/product/761/pil",
    "Seretide": "https://www.medicines.org.uk/emc/product/76/pil",
    "Avodart": "https://www.medicines.org.uk/emc/product/4189/pil"
}

# Language Selection
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

            Suggest the following for the GSK Brand {brand}:
            1. Three probing questions the rep should ask the doctor.
            2. Recommended communication style for this profile.
            3. Most suitable sales module.

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
        "segments": ["باحث عن الأدلة", "مشَكّك", "مضغوط بالوقت", "مُبكر التبني", "تقليدي"],
        "behaviors": ["علمي", "مشَكّك", "سلبي", "عاطفي", "مجادل"],
        "objectives": ["زيادة الوعي", "التعامل مع الاعتراضات", "متابعة", "إطلاق جديد", "تذكير"],
        "system_prompt": "أنت مساعد خبير في مبيعات الأدوية مدعوم بالذكاء الاصطناعي.",
        "user_prompt": """
            أنت مساعد خبير في مبيعات الأدوية مدعوم بالذكاء الاصطناعي.

            بناءً على:
            - نوع الطبيب: {segment}
            - سلوك الطبيب: {behavior}
            - هدف الزيارة: {objective}

            اقترح التالي لمنتج GSK {brand}:
            1. ثلاثة أسئلة استكشافية يمكن للمندوب طرحها على الطبيب.
            2. أسلوب التواصل الأنسب لهذا النوع من الأطباء.
            3. الوحدة البيعية الأنسب لهذه الحالة.

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

if st.button(t["generate"]):
    with st.spinner(t["loading"]):
        prompt = t["user_prompt"].format(segment=segment, behavior=behavior, objective=objective, brand=brand)

        response = client.chat.completions.create(
            model="llama3-70b-8192",  # ✅ Use valid Groq model
            messages=[
                {"role": "system", "content": t["system_prompt"]},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        ai_output = response.choices[0].message.content
        st.subheader(t["result_title"])
        st.markdown(ai_output)

        # Add leaflet link
        leaflet_url = gsk_brands[brand]
        st.markdown(f"[{t['leaflet']} - {brand}]({leaflet_url})")
