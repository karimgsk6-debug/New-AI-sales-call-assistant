import streamlit as st
import groq
from groq import Groq

# Initialize Groq client with your API key
client = Groq(
    api_key="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",)

# Define GSK's approved selling approaches
gsk_approaches = [
    "Awareness & Disease Education",
    "Product Efficacy & Clinical Evidence",
    "Safety Profile & Tolerability",
    "Dosing & Administration",
    "Patient Support & Adherence",
    "Objection Handling"
]

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
        "generate": "Generate AI Suggestions",
        "loading": "Generating recommendations...",
        "result_title": "🤖 AI Recommendations",
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

            Your tasks:
            1. Suggest **three probing questions** aligned with the most relevant GSK selling approach.
            2. Recommend a **communication style** that matches the doctor’s profile and the chosen approach.
            3. Select **ONE selling approach only** from the approved list above and explain why it is the best fit.
            4. Adapt your suggestions so they remain fully compliant with the approved GSK sales approaches.

            Be specific, concise, and practical.
        """
    },
    "العربية": {
        "title": "🧠 مساعد الزيارات الطبية بالذكاء الاصطناعي",
        "description": "استعد لزيارة الأطباء باقتراحات مدعومة بالذكاء الاصطناعي.",
        "select_segment": "اختر نوع الطبيب:",
        "select_behavior": "اختر سلوك الطبيب:",
        "select_objective": "اختر هدف الزيارة:",
        "generate": "احصل على الاقتراحات",
        "loading": "جاري توليد الاقتراحات...",
        "result_title": "🤖 اقتراحات الذكاء الاصطناعي",
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

            المطلوب:
            1. اقترح **ثلاثة أسئلة استكشافية** مرتبطة بأسلوب البيع الأنسب.
            2. أوصِ بـ **أسلوب التواصل** الأنسب الذي يتماشى مع ملف الطبيب والأسلوب المختار.
            3. اختر **أسلوب بيع واحد فقط** من القائمة أعلاه ووضح لماذا هو الأنسب.
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

# Include the GSK brand name
brand = "Augmentin"

if st.button(t["generate"]):
    with st.spinner(t["loading"]):
        modules_str = "\n".join(gsk_approaches)
        prompt = t["user_prompt"].format(
            segment=segment,
            behavior=behavior,
            objective=objective,
            brand=brand,
            approaches=modules_str
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
