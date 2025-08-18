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

# --- Brand logos (mix of local and URL) ---
gsk_brands_images = {
    "Augmentin": "images/augmentin.png",  
    "Shingrix": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Shingrix_logo.png/320px-Shingrix_logo.png",  # URL logo
    "Seretide": "images/seretide.png",
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

# --- Load brand image safely ---
image_path = gsk_brands_images.get(brand)
try:
    if image_path.startswith("http"):  # Load from URL
        response = requests.get(image_path)
        img = Image.open(BytesIO(response.content))
    else:  # Load local file
        img = Image.open(image_path)
    st.image(img, width=200)
except
