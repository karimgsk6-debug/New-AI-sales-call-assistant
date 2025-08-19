import streamlit as st  
from PIL import Image
import requests
from io import BytesIO
import groq
from groq import Groq

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

# --- Brand logos (mix of local and URL) ---
gsk_brands_images = {
    "Augmentin": "images/augmentin.png",
    "Shingrix": "https://www.oma-apteekki.fi/WebRoot/NA/Shops/na/67D6/48DA/D0B0/D959/ECAF/0A3C/0E02/D573/3ad67c4e-e1fb-4476-a8a0-873423d8db42_3Dimage.png",
    "Seretide": "images/seretide.png",
}

# --- RACE Segmentation ---
race_segments = [
    "R – Relationship Oriented: Focuses on building trust and personal connection.",
    "A – Active Prescriber: Already prescribing, open to increasing usage with right support.",
    "C – Conservative: Cautious, prefers established treatments, resistant to change.",
    "E – Evidence Seeker: Requires strong data, guidelines, and scientific evidence."
]

# --- Doctor Barriers ---
doctor_barriers = [
    "1 - HCP does not consider HZ as risk for the selected patient profile",
    "2 - HCP thinks there is no time to discuss preventive measures with the patients",
    "3 - HCP thinks about cost considerations",
    "4 - HCP is not convinced that HZ Vx is effective in reducing the burden",
    "5 - Accessibility (POVs)"
]

# --- Other filters ---
objectives = ["Awareness", "Adoption", "Retention"]
specialties = ["General Practitioner", "Cardiologist", "Dermatologist", "Endocrinologist", "Pulmonologist"]

# --- Approved sales approaches ---
gsk_approaches = [
    "Use data-driven evidence",
    "Focus on patient outcomes",
    "Leverage storytelling techniques",
]

# --- Page layout ---
st.title("🧠 AI Sales Call Assistant")
brand = st.selectbox("Select Brand / اختر العلامة التجارية", options=list(gsk_brands.keys()))

# --- Load brand image safely ---
image_path = gsk_brands_images.get(brand)
try:
    if image_path.startswith("http"):
        response = requests.get(image_path)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(image_path)
    st.image(img, width=200)
except Exception:
    st.warning(f"⚠️ Could not load image for {brand}. Using placeholder.")
    st.image("https://via.placeholder.com/200x100.png?text=No+Image", width=200)

# --- Inputs ---
segment = st.selectbox("Select RACE Segment / اختر شريحة RACE", race_segments)
barrier = st.selectbox("Select Doctor Barrier / اختر حاجز الطبيب", doctor_barriers)
objective = st.selectbox("Select Objective / اختر الهدف", objectives)
specialty = st.selectbox("Select Doctor Specialty / اختر تخصص الطبيب", specialties)

# --- Clear chat button ---
if st.button("🗑️ Clear Chat / مسح المحادثة"):
    st.session_state.chat_history = []

# --- Chat container ---
chat_container = st.container()

# --- User message input ---
placeholder_text = "Type your message..." if language == "English" else "اكتب رسالتك..."
user_input = st.text_area(placeholder_text, key="user_input", height=80)

if st.button("🚀 Send / أرسل") and user_input.strip():
    with st.spinner("Generating AI response... / جارٍ إنشاء الرد"):
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Prepare dynamic GSK approaches context
        approaches_str = "\n".join(gsk_approaches)

        # Build AI prompt with Doctor Barrier
        prompt = f"""
Language: {language}
You are an expert GSK sales assistant. 
User input: {user_input}
RACE Segment: {segment}
Doctor Barrier: {barrier}
Objective: {objective}
Brand: {brand}
Doctor Specialty: {specialty}
Approved GSK Sales Approaches:
{approaches_str}
Provide actionable suggestions in a friendly, professional tone.
"""

        # Call Groq API
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

# --- Leaflet link below chat ---
st.markdown(f"[Brand Leaflet - {brand}]({gsk_brands[brand]})")
