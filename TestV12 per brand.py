import streamlit as st
from st_audiorec import st_audiorec
import tempfile
from groq import Groq

# --------------------
# Streamlit Page Setup
# --------------------
st.set_page_config(page_title="🧠 AI Sales Call Assistant", layout="centered")

# --------------------
# Groq Client Setup
# --------------------
client = Groq(api_key=st.secrets["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"])

# --------------------
# Session State Init
# --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --------------------
# Language Filter
# --------------------
lang = st.radio("🌐 Select Language / اختر اللغة", ["English", "العربية"], horizontal=True)

# --------------------
# Input Filters
# --------------------
brand = st.selectbox("Select Brand / اختر العلامة التجارية", ["Augmentin", "Shingrix", "Seretide"])
specialty = st.selectbox("Select Doctor Specialty / اختر تخصص الطبيب", 
                         ["General Practitioner", "Cardiologist", "Dermatologist", "Pulmonologist", "Other"])
segment = st.selectbox("Select Segment / اختر الفئة", ["Evidence-Seeker", "Relationship-Oriented", "Skeptic"])
behavior = st.selectbox("Select Behavior / اختر السلوك", ["Scientific", "Emotional", "Logical"])
objective = st.selectbox("Select Objective / اختر الهدف", ["Awareness", "Trial", "Adoption"])

# --------------------
# 🎤 Voice Input (st_audiorec)
# --------------------
st.markdown("🎤 Speak your input:")
wav_audio_data = st_audiorec()

user_message = None
if wav_audio_data is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        audio_path = tmpfile.name

    st.audio(audio_path, format="audio/wav")

    # ---- Speech-to-Text with Groq Whisper ----
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f,
            response_format="text"
        )
    user_message = transcript
    st.success(f"📝 Transcribed: {user_message}")

# --------------------
# Manual Input Fallback
# --------------------
user_text = st.text_input("Or type your input here / أو اكتب هنا")

# --------------------
# Process Input
# --------------------
if st.button("Send / إرسال"):
    if user_message:  # from voice
        final_message = f"{user_message} | Segment: {segment}, Behavior: {behavior}, Objective: {objective}, Brand: {brand}, Specialty: {specialty}, Language: {lang}"
    elif user_text.strip():
        final_message = f"{user_text} | Segment: {segment}, Behavior: {behavior}, Objective: {objective}, Brand: {brand}, Specialty: {specialty}, Language: {lang}"
    else:
        final_message = None

    if final_message:
        # Save user input
        st.session_state.chat_history.append({"role": "user", "content": final_message})

        # --- Example AI Call (placeholder for now) ---
        ai_output = f"✅ Suggested approach for {brand} with {specialty} ({segment}, {behavior}, {objective}) - Based on input: {final_message}"
        
        st.session_state.chat_history.append({"role": "ai", "content": ai_output})

# --------------------
# Display Chat History
# --------------------
for msg in st.session_state.chat_history:
    role = "You" if msg["role"] == "user" else "AI"
    st.markdown(f"**{role}:** {msg['content']}")
