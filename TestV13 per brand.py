import streamlit as st
from groq import Groq

# -----------------------------
# Secure Groq API key setup
# -----------------------------
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["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"])
else:
    st.error("🚨 Missing GROQ_API_KEY in Streamlit secrets.")
    client = None

# -----------------------------
# App Title
# -----------------------------
st.title("🧠 AI Sales Call Assistant – GSK")
st.markdown("Prepare for HCP visits with AI-powered suggestions tailored by **RACE segmentation**, specialty, and brand.")

# -----------------------------
# RACE Segmentation
# -----------------------------
st.subheader("🎯 Select RACE Segmentation")
st.markdown("""
**RACE Definitions**  
- 🟢 **R (Relationship Seeker):** Values trust and partnership, prefers collaborative discussions.  
- 🔵 **A (Active Supporter):** Engaged, already positive toward the brand, seeks tools and reinforcement.  
- 🟠 **C (Challenger):** Questions data, skeptical, requires strong evidence and logic.  
- 🟣 **E (Evidence Seeker):** Focused on clinical proof, guidelines, and trial outcomes.  
""")

race_segments = [
    "Relationship Seeker (R)",
    "Active Supporter (A)",
    "Challenger (C)",
    "Evidence Seeker (E)"
]
race_segment = st.selectbox("Choose RACE Segment", options=race_segments)

# -----------------------------
# Doctor Specialty
# -----------------------------
st.subheader("👨‍⚕️ Select Doctor Specialty")
specialties = ["General Practitioner", "Dermatologist", "Pulmonologist", "Cardiologist", "Other"]
specialty = st.selectbox("Choose Specialty", options=specialties)

# -----------------------------
# Brand Selection
# -----------------------------
st.subheader("💊 Select Brand")
brands = ["Augmentin", "Shingrix", "Seretide"]
brand = st.selectbox("Choose Brand", options=brands)

# -----------------------------
# Sales Objective
# -----------------------------
st.subheader("🎯 Define Sales Objective")
objectives = [
    "Raise awareness",
    "Address objections",
    "Reinforce brand value",
    "Encourage trial/adoption",
    "Support adherence"
]
objective = st.selectbox("Choose Objective", options=objectives)

# -----------------------------
# Chat Display Function
# -----------------------------
def display_chat(user_message, ai_message):
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        st.markdown(ai_message)

# -----------------------------
# Generate AI Suggestion
# -----------------------------
if st.button("✨ Generate Sales Call Suggestion"):
    if client:
        prompt = f"""
        You are an AI assistant helping a pharma sales rep prepare for a doctor visit. 
        Doctor Segment: {race_segment}  
        Specialty: {specialty}  
        Brand: {brand}  
        Objective: {objective}  

        Provide probing questions, tailored communication style, and a suggested sales call flow 
        following GSK’s approved selling approaches.
        """
        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            ai_reply = response.choices[0].message["content"]
            display_chat(prompt, ai_reply)
        except Exception as e:
            st.error(f"❌ Error generating response: {e}")
    else:
        st.warning("⚠️ API client not initialized. Please check your secrets.")
