import streamlit as st
from st_audiorec import st_audiorec
from groq import Groq
import base64
import tempfile
import os

# --- Initialize Groq client ---
client = Groq(api_key="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")

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Language selector ---
language = st.radio("Select Language / اختر اللغة", options=["English", "العربية"])

# --- GSK brand mappings ---
gsk_brands = {
    "Augmentin": "https://example.com/augmentin-leaflet",
    "Shingrix": "https://example.com/shingrix-leaflet",
    "Seretide": "https://example.com/seretide-leaflet",
}

# --- Example filters ---
segments = ["Evidence-Seeker", "Skeptic", "Relationship-Oriented"]
behaviors = ["Scientific", "Emotional", "Logical"]
objectives = ["Awareness", "Adoption", "Retention"]
specialties = ["General Practitioner", "Cardiologist", "Dermatologist", "Endocrinologist", "Pulmonologist"]

# Approved sales approaches (replace with your official list)
gsk_approaches = [
    "Use data-driven evidence",
    "Focus on patient outcomes",
    "Leverage storytelling techniques",
]

# --- Page layout ---
st.title("🧠 AI Sales Call Assistant")
brand = st.selectbox("Select Brand / اختر العلامة التجارية", options=list(gsk_brands.keys()))

# --- Inputs ---
segment = st.selectbox("Select Segment / اختر الشريحة", segments)
behavior = st.selectbox("Select Behavior / اختر السلوك", behaviors)
objective = st.selectbox("Select Objective / اختر الهدف", objectives)
specialty = st.selectbox("Select Doctor Specialty / اختر تخصص الطبيب", specialties)

# --- Clear chat button ---
if st.button("🗑️ Clear Chat / مسح المحادثة"):
    st.session_state.chat_history = []

# --- Chat container ---
chat_container = st.container()

# --- Text input ---
placeholder_text = "Type your message..." if language == "English" else "اكتب رسالتك..."
user_input = st.text_area(placeholder_text, key="user_input", height=80)

# --- Voice input ---
st.markdown("🎤 Or speak your message:")
wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        audio_file_path = tmpfile.name

    # Transcribe with Groq Whisper
    with open(audio_file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f
        )
    user_input = transcription.text
    st.success(f"🎙️ You said: {user_input}")

# --- Handle send ---
if st.button("🚀 Send / أرسل") and user_input.strip():
    with st.spinner("Generating AI response... / جارٍ إنشاء الرد"):
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Build context
        approaches_str = "\n".join(gsk_approaches)
        prompt = f"""
        Language: {language}
        You are an expert GSK sales assistant. 
        User input: {user_input}
        Segment: {segment}
        Behavior: {behavior}
        Objective: {objective}
        Brand: {brand}
        Doctor Specialty: {specialty}
        Approved GSK Sales Approaches:
        {approaches_str}
        Provide actionable suggestions in a friendly, professional tone.
        """

        # Call Groq LLM
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": f"You are a helpful sales assistant chatbot that responds in {language}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        ai_output = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "ai", "content": ai_output})

        # --- TTS (AI voice output) ---
        tts_response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",  # Options: alloy, verse, etc.
            input=ai_output
        )

        # Save & play audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmpfile.write(tts_response.read())
            audio_path = tmpfile.name

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            b64 = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
            <audio autoplay controls>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

# --- Display chat history ---
with chat_container:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style="
                    text-align:right;
                    margin:10px 0;
                    padding:10px;
                    background-color:#d1e7dd;
                    border-radius:12px;
                    display:inline-block;
                    max-width:80%;
                    white-space:pre-wrap;
                ">
                <strong>You:</strong><br>{msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="
                    text-align:left;
                    margin:10px 0;
                    padding:15px;
                    background-color:#f0f2f6;
                    border-radius:12px;
                    display:inline-block;
                    max-width:80%;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    white-space:pre-wrap;
                ">
                <strong>AI:</strong><br>{msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

# --- Leaflet link below chat ---
st.markdown(f"[Brand Leaflet - {brand}]({gsk_brands[brand]})")
