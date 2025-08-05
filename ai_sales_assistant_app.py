import streamlit as st
from openai import OpenAI

# ✅ استخدم st.secrets لتأمين المفتاح
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.set_page_config(page_title="AI Sales Call Assistant", page_icon="🧠")

st.title("🧠 AI Sales Call Assistant")
st.markdown("احصل على اقتراحات ذكية بناءً على شخصية الطبيب وسلوكه وهدف الزيارة.")

segments = ["Evidence‑Seeker", "Relationship‑Oriented", "Skeptic"]
behaviors = ["Scientific", "Emotional", "Logical"]
objectives = ["Awareness", "Objection Handling", "Follow‑up"]

segment = st.selectbox("🧬 Doctor Segment", segments)
behavior = st.selectbox("🧠 Doctor Behavior", behaviors)
objective = st.selectbox("🎯 Visit Objective", objectives)

if st.button("🔍 Generate AI Suggestions"):
    with st.spinner("Generating..."):
        prompt = f"""
You are an expert pharma sales assistant AI.
Based on:
- Segment: {segment}
- Behavior: {behavior}
- Visit Objective: {objective}

Provide:
1. 3 probing questions
2. Communication style
3. Recommended module
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        result = response.choices[0].message.content
        st.subheader("🤖 AI Recommendations")
        st.markdown(result)
