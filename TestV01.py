import streamlit as st
import groq
from groq import Groq

client = Groq(
    api_key="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",
)
# Streamlit UI
st.title("🧠 AI Sales Call Assistant")

st.markdown("Prepare for HCP visits with AI-powered suggestions.")

# Input options
segments = ["Evidence-Seeker", "Skeptic", "Time-Pressured", "Early Adopter", "Traditionalist"]
behaviors = ["Scientific", "Skeptical", "Passive", "Emotional", "Argumentative"]
objectives = ["Awareness", "Objection Handling", "Follow-up", "New Launch", "Reminder"]

segment = st.selectbox("Select Doctor Segment:", segments)
behavior = st.selectbox("Select Doctor Behavior:", behaviors)
objective = st.selectbox("Select Visit Objective:", objectives)

# Generate AI Recommendations
if st.button("Generate AI Suggestions"):
    with st.spinner("Generating recommendations..."):
        prompt = f"""
        You are an expert pharma sales assistant AI.

        Based on:
        - Segment: {segment}
        - Behavior: {behavior}
        - Visit Objective: {objective}

        Suggest the following:
        1. Three probing questions the rep should ask the doctor.
        2. Recommended communication style for this profile.
        3. Most suitable sales module.

        Be specific, concise, and practical.
        """

        response = client.chat.completions.create(
           model="llama3-8b-8192",
            messages=[
        {
            "role": "system",
            "content": "You are an expert pharma sales assistant AI."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
            temperature=0.7
        )

        ai_output = response.choices[0].message.content
        st.subheader("🤖 AI Recommendations")
        st.markdown(ai_output)
