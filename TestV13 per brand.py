import streamlit as st
from groq import Groq

# Initialize Groq client
client = Groq(api_key=st.secrets["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"])

# Title & Branding
st.image("brand_logo.png", width=120)  # replace with your logo file in same folder
st.title("🧠 AI Sales Call Assistant")
st.markdown("Prepare for HCP visits with AI-powered suggestions, aligned with **RACE Segmentation**.")

# Define RACE segmentation
race_segments = {
    "Reach": "Did not start to prescribe yet. Don't believe that vaccination is his responsibility.",
    "Acquisition": "Prescribe to patient who initiate discussion about the vaccine. Convinced about Shingrix data.",
    "Conversion": "Proactively initiate discussion with specific patient profile. For other patient profiles, he is not prescribing yet.",
    "Engagement": "Proactively prescribe to different patient profiles."
}

# Streamlit UI
segment = st.selectbox(
    "🎯 Select HCP Segment (RACE):",
    options=list(race_segments.keys()),
    format_func=lambda x: f"{x} – {race_segments[x]}"
)

behavior = st.selectbox(
    "🧩 Select Customer Behavior:",
    ["Scientific", "Emotional", "Logical"]
)

objective = st.selectbox(
    "🎯 Select Sales Call Objective:",
    ["Awareness", "Conviction", "Action"]
)

if st.button("🚀 Generate Call Guidance"):
    with st.spinner("Generating AI suggestion..."):
        prompt = f"""
        You are a pharma sales mentor. 
        The HCP belongs to the **{segment}** segment:
        {race_segments[segment]}

        Behavior: {behavior}
        Objective: {objective}

        Suggest probing questions, communication style, and sales approach (aligned with GSK approved RACE selling strategy).
        """
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )
        st.markdown("### 💡 Suggested Approach")
        st.write(response.choices[0].message.content)
