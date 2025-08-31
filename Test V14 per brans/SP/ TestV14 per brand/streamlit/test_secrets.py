import streamlit as st
from groq import Groq

st.title("🧪 Test Groq API Key")

try:
    api_key = st.secrets["GROQ"]["API_KEY"]
    st.success("✅ Groq API key found!")
    st.write("First 5 chars:", api_key[:5] + "...")
except KeyError as e:
    st.error(f"❌ Could not find Groq API key: {e}")

# Optional: test Groq client
try:
    client = Groq(api_key=api_key)
    st.success("Groq client initialized successfully!")
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
