import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
import base64
import os

# --- Initialize Groq client ---
client = Groq(api_key=st.secrets["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"])

# --- Language filter ---
language = st.radio("🌐 Select Language / اختر اللغة", ["English", "العربية"])
if language == "English":
    t = {
        "send": "Send",
        "loading": "Generating response...",
        "system_prompt": "You are a GSK sales call assistant helping reps with call approaches.",
        "user_prompt": "Doctor Specialty: {specialty}\nSegment: {segment}\nBehavior: {behavior}\nObjective: {objective}\nBrand: {brand}\n\nGenerate tailored suggestions based on approved GSK sales approaches.",
        "leaflet": "View Product Leaflet",
        "play_again": "🔊 Play Again"
    }
    tts_lang = "en"
else:
    t = {
        "send": "إرسال",
        "loading": "جاري إنشاء الاستجابة...",
        "system_prompt": "أنت مساعد مكالمات مبيعات من GSK تساعد المندوبين في طرق البيع المعتمدة.",
        "user_prompt": "تخصص الطبيب: {specialty}\nالشريحة: {segment}\nالسلوك: {behavior}\nالهدف: {objective}\nالعلامة التجارية: {brand}\n\nقم بإنشاء اقتراحات مخصصة استنادًا إلى طرق البيع المعتمدة من GSK.",
        "leaflet": "عرض النشرة",
        "play_again": "🔊 إعادة التشغيل"
    }
    tts_lang = "ar"

# --- Define dropdown options ---
gsk_brands = {
    "Augmentin": "https://www.medicines.org.uk/emc/product/1049/smpc",
    "Shingrix": "https://www.ema.europa.eu/en/medicines/human/EPAR/shingrix",
    "Seretide": "https://www.medicines.org.uk/emc/product/4498/smpc"
}

segments = ["Evidence-Seeker", "Relationship-Oriented", "Skeptic"]
behaviors = ["Scientific", "Emotional", "Logical"]
objectives = ["Awareness", "Convince", "Reinforce"]
specialties = ["GP", "Dermatologist", "Pulmonologist", "Other"]

# --- User selections ---
brand = st.selectbox("Select Brand / اختر العلامة التجارية", options=list(gsk_brands.keys()))
specialty = st.selectbox("Select Doctor Specialty / اختر تخصص الطبيب", options=specialties)
segment = st.selectbox("Select Segment / اختر الشريحة", options=segments)
behavior = st.selectbox("Select Behavior / اختر السلوك", options=behaviors)
objective = st.selectbox("Select Objective / اختر الهدف", options=objectives)

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- Clear chat button ---
if st.button("🗑️ Clear Chat / مسح المحادثة"):
    st.session_state.chat_history = []
    st.session_state.last_audio = None

# --- Chat container ---
chat_container = st.container()

# --- Voice Input ---
st.markdown("🎙️ Speak your message instead of typing:")
voice_text = mic_recorder(start_prompt="Start recording", stop_prompt="Stop recording", just_once=True, use_container_width=True)

# If voice was recorded, set it as user input
if voice_text and "text" in voice_text and voice_text["text"].strip() != "":
    user_input = voice_text["text"]
else:
    user_input = st.text_input("💬 Enter your message (optional)")

# --- Send button ---
if st.button(t["send"]):
    with st.spinner(t["loading"]):
        # Store user input in chat history
        user_message = f"Segment: {segment}, Behavior: {behavior}, Objective: {objective}, Brand: {brand}, Specialty: {specialty}\nUser said: {user_input}"
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        # Prepare AI prompt
        prompt = t["user_prompt"].format(
            specialty=specialty,
            segment=segment,
            behavior=behavior,
            objective=objective,
            brand=brand,
        ) + f"\n\nDoctor Input: {user_input}"

        # Call Groq API
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": t["system_prompt"]},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        ai_output = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "ai", "content": ai_output})

        # --- Text-to-Speech (gTTS) ---
        tts = gTTS(ai_output, lang=tts_lang)
        tts.save("ai_response.mp3")

        with open("ai_response.mp3", "rb") as f:
            audio_bytes = f.read()
        st.session_state.last_audio = base64.b64encode(audio_bytes).decode()

        # Autoplay AI response
        audio_html = f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{st.session_state.last_audio}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# --- Play Again button ---
if st.session_state.last_audio and st.button(t["play_again"]):
    audio_html = f"""
    <audio autoplay controls>
        <source src="data:audio/mp3;base64,{st.session_state.last_audio}" type="audio/mp3">
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
                    font-family:sans-serif;
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
                    font-family:sans-serif;
                    white-space:pre-wrap;
                ">
                <strong>AI:</strong><br>{msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

# --- Product leaflet link ---
st.markdown(f"[{t['leaflet']} - {brand}]({gsk_brands[brand]})")
