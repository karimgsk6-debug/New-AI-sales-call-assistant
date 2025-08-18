import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import groq
from groq import Groq

# Initialize Groq client with your API key
client = Groq(api_key="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",)

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

gsk_brands_images = {
    "Augmentin": "images/augmentin.png",  # local or URL
    "Shingrix": "images/shingrix.png",
    "Seretide": "images/seretide.png",
}

# --- Example segments, behaviors, objectives, and approaches ---
segments = ["Evidence-Seeker", "Skeptic", "Relationship-Oriented"]
behaviors = ["Scientific", "Emotional", "Logical"]
objectives = ["Awareness", "Adoption", "Retention"]
gsk_approaches = [
    "Use data-driven evidence",
    "Focus on patient outcomes",
    "Leverage storytelling techniques",
]

# --- Page layout ---
st.title("🧠 AI Sales Call Assistant")
brand = st.selectbox(
    "Select Brand / اختر العلامة التجارية", options=list(gsk_brands.keys())
)

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
segment = st.selectbox(
    "Select Segment / اختر الشريحة", segments
)
behavior = st.selectbox(
    "Select Behavior / اختر السلوك", behaviors
)
objective = st.selectbox(
    "Select Objective / اختر الهدف", objectives
)

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
        # Append user input to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Prepare dynamic GSK approaches context
        approaches_str = "\n".join(gsk_approaches)

        # Build AI prompt with language context
        prompt = f"""
        Language: {language}
        You are an expert GSK sales assistant. 
        User input: {user_input}
        Segment: {segment}
        Behavior: {behavior}
        Objective: {objective}
        Brand: {brand}
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
