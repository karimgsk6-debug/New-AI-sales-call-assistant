import streamlit as st
import groq
from groq import Groq

client = Groq(api_key="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")  # Add your API key here

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

            Suggest the following for the GSK Brand Augmentin:
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
        "generate": "احصل على الاقتراحات",
        "loading": "جاري توليد الاقتراحات...",
        "result_title": "🤖 اقتراحات الذكاء الاصطناعي",
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

            اقترح التالي:
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

if st.button(t["generate"]):
    with st.spinner(t["loading"]):
        prompt = t["user_prompt"].format(segment=segment, behavior=behavior, objective=objective)

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
