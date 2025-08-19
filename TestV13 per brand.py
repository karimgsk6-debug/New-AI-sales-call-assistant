import streamlit as st
from groq import Groq

# -------------------------------
# API Key Safe Check
# -------------------------------
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["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"])
else:
    st.error("🚨 Missing GROQ_API_KEY in Streamlit secrets. Please add it in `.streamlit/secrets.toml`")
    client = None

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🧠 AI Sales Call Assistant")
st.markdown("Prepare for HCP visits with AI-powered suggestions.")

# Segments (RACE Model for Shingrix)
segments = {
    "Reach": "Did not start to prescribe yet. Don't believe vaccination is their responsibility.",
    "Acquisition": "Prescribe to patients who initiate discussion about the vaccine. Convinced about Shingrix data.",
    "Conversion": "Proactively initiate discussion with specific patient profiles. For other profiles, not prescribing yet.",
    "Engagement": "Proactively prescribe to different patient profiles."
}

behaviors = ["Evidence-Seeker", "Skeptic", "Time-Pressured", "Relationship-Oriented"]
objectives = ["Awareness", "Education", "Conversion", "Retention"]

# -------------------------------
# Input Options
# -------------------------------
st.subheader("🔹 Select Customer Profile")

segment = st.selectbox("Choose RACE Segment", list(segments.keys()))
behavior = st.selectbox("Choose Behavior Type", behaviors)
objective = st.selectbox("Choose Call Objective", objectives)

# -------------------------------
# Generate Suggestions
# -------------------------------
if st.button("💡 Generate Call Guidance"):
    if client:
        prompt = f"""
        You are an AI assistant for pharmaceutical sales reps.
        The rep is preparing for a doctor visit.

        Segment (RACE Model): {segment} → {segments[segment]}
        Behavior Type: {behavior}
        Call Objective: {objective}

        Task: 
        - Suggest tailored probing questions
        - Recommend communication style
        - Suggest the most relevant GSK-approved selling module
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=400
            )
            answer = response.choices[0].message.content
            st.success("✅ Suggested Call Guidance")
            st.write(answer)
        except Exception as e:
            st.error(f"Error generating response: {e}")
    else:
        st.warning("⚠️ Cannot generate guidance because API key is missing.")

# -------------------------------
# RACE Segmentation Reference
# -------------------------------
with st.expander("📌 RACE Segmentation Reference"):
    st.markdown("""
    **R – Reach**: Did not start prescribing yet, don’t believe vaccination is their responsibility.  
    **A – Acquisition**: Prescribe to patients who initiate discussion, convinced about Shingrix data.  
    **C – Conversion**: Proactively initiate discussion with specific patient profiles, but not prescribing for all.  
    **E – Engagement**: Proactively prescribe to different patient profiles.  
    """)
