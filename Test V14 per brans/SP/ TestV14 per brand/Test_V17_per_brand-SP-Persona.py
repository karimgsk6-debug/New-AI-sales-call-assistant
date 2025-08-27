import streamlit as st
from groq import Groq
import requests
from datetime import datetime

# --- Groq API key directly in code ---
client = Groq(api_key="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")

# --- Brand scripts dictionary ---
brand_scripts = {
    "Shingrix": "https://raw.githubusercontent.com/karimgsk6-debug/New-AI-sales-call-assistant/main/Test%20V14%20per%20brans/SP/TestV14%20per%20brand/Test_V17_per_brand-SP-Persona.py",
    # Add other brands if needed
}

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
brand = st.sidebar.selectbox("Select Brand", list(brand_scripts.keys()))
hcp_segments = st.sidebar.multiselect(
    "Select HCP Segments", 
    ["Potential", "Adopter", "Laggard", "Brand Supporter", "Competitor Supporter"]
)
hcp_barriers = st.sidebar.multiselect(
    "Select HCP Barriers", 
    ["Awareness", "Cost", "Efficacy Concerns", "Side Effects", "No Time", "Not Priority"]
)
language = st.sidebar.radio("Language", ["English", "Arabic"])
if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state.chat_history = []

st.title("💬 AI Sales Call Assistant")

# --- Load & display Python file ---
script_url = brand_scripts[brand]
script_text = ""

try:
    r = requests.get(script_url)
    r.raise_for_status()
    script_text = r.text

    with st.expander("📄 Extracted Script Content", expanded=False):
        st.text(script_text[:2000])  # limit preview to first 2000 chars

except Exception as e:
    st.error(f"⚠️ Could not fetch or parse script: {e}")
    st.markdown(f"👉 [Open file manually]({script_url})")

# --- Chat interface ---
user_input = st.text_input("💭 Ask your question:")

if user_input:
    prompt = f"""
You are a sales assistant helping with brand {brand}.
HCP Segments: {', '.join(hcp_segments) if hcp_segments else 'None'}
HCP Barriers: {', '.join(hcp_barriers) if hcp_barriers else 'None'}
Language: {language}
Reference Script Content: {script_text[:2000]}  # limit to avoid huge context

Question: {user_input}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        answer = response.choices[0].message.content.strip()
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", answer))
    except Exception as e:
        st.error(f"❌ Chatbot error: {e}")

# --- Display chat history ---
for sender, msg in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {msg}")
