import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from groq import Groq
import streamlit.components.v1 as components
import re
from docx import Document
from io import BytesIO

# --- Hardcoded Groq API key ---
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"  # Replace with your Groq API key
client = Groq(api_key="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")

# --- Disclaimer ---
st.markdown(
    """
    ⚠️ **Disclaimer:**  
    This AI-powered assistant is designed to **support sales representatives** in preparing and tailoring sales calls.  
    It is **not a replacement for medical or professional judgment**. Always follow company guidelines and approved selling approaches.
    """,
    unsafe_allow_html=True
)

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "brand" not in st.session_state:
    st.session_state.brand = ""
if "segment" not in st.session_state:
    st.session_state.segment = ""
if "barrier" not in st.session_state:
    st.session_state.barrier = []
if "objective" not in st.session_state:
    st.session_state.objective = ""
if "specialty" not in st.session_state:
    st.session_state.specialty = ""
if "persona" not in st.session_state:
    st.session_state.persona = ""
if "response_length" not in st.session_state:
    st.session_state.response_length = "Medium"
if "response_tone" not in st.session_state:
    st.session_state.response_tone = "Formal"
if "language" not in st.session_state:
    st.session_state.language = "English"

# --- Language selector ---
st.session_state.language = st.radio("Select Language / اختر اللغة", options=["English", "العربية"], index=0 if st.session_state.language=="English" else 1)

# --- GSK logo ---
logo_local_path = "images/gsk_logo.png"
logo_fallback_url = "https://www.tungsten-network.com/wp-content/uploads/2020/05/GSK_Logo_Full_Colour_RGB.png"

col1, col2 = st.columns([1, 5])
with col1:
    try:
        logo_img = Image.open(logo_local_path)
        st.image(logo_img, width=120)
    except Exception:
        st.image(logo_fallback_url, width=120)
with col2:
    st.title("🧠 AI Sales Call Assistant")

# --- Brands ---
gsk_brands = {
    "Trelegy": "https://example.com/trelegy-leaflet",
    "Shingrix": "https://assets.gskinternet.com/pharma/GSKpro/Egypt/Shingrix/pm_eg_sgx_eml_240052_reconstitution%20Safety.pdf",
    "Zejula": "https://assets.gskinternet.com/pharma/GSKpro/Egypt/Zejula/zejula_approved_abbreviated_prescribing_information.pdf",
}
gsk_brands_images = {
    "Trelegy": "https://mimsshst.blob.core.windows.net/drug-resources/ID/packshot/Trelegy%20Ellipta6001PPS0.JPG",
    "Shingrix": "https://www.oma-apteekki.fi/WebRoot/NA/Shops/na/67D6/48DA/D0B0/D959/ECAF/0A3C/0E02/D573/3ad67c4e-e1fb-4476-a8a0-873423d8db42_3Dimage.png",
    "Zejula": "https://lh4.googleusercontent.com/proxy/wpBMIGLXVD6wGuk-FizVEUf_2mQWbt6m0pShWWovQMQXQ4f1mWceGSCSqm7q6MJi0Boe7nvlIGuaRzelL376fw2vaNgc9QprmGJaXpe-945WLiIEuR0-ZzYn0Q",
}

# --- RACE Segmentation ---
race_segments = [
    "R – Reach: Did not start to prescribe yet and Don't believe that vaccination is his responsibility.",
    "A – Acquisition: Prescribe to patient who initiate discussion about the vaccine but Convinced about Shingrix data.",
    "C – Conversion: Proactively initiate discussion with specific patient profile but For other patient profiles he is not prescribing yet.",
    "E – Engagement: Proactively prescribe to different patient profiles"
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

# --- HCP Personas ---
personas = [
    "Uncommitted Vaccinator – Not engaged, poor knowledge, least likely to prescribe vaccines (26%)",
    "Reluctant Efficiency – Do not see vaccinating 50+ as part of role, least likely to believe in impact (12%)",
    "Patient Influenced – Aware of benefits but prescribes only if patient requests (26%)",
    "Committed Vaccinator – Very positive, motivated, prioritizes vaccination & sets example (36%)"
]

# --- Approved sales approaches ---
gsk_approaches = [
    "Use data-driven evidence",
    "Focus on patient outcomes",
    "Leverage storytelling techniques",
]

# --- Sales Call Flow ---
sales_call_flow = ["Prepare", "Engage", "Create Opportunities", "Influence", "Drive Impact", "Post Call Analysis"]

# --- Sidebar Filters ---
st.sidebar.header("Filters & Options")

# Reset Selections
if st.sidebar.button("🔄 Reset Selections"):
    st.session_state.brand = ""
    st.session_state.segment = ""
    st.session_state.barrier = []
    st.session_state.objective = ""
    st.session_state.specialty = ""
    st.session_state.persona = ""
    st.session_state.response_length = "Medium"
    st.session_state.response_tone = "Formal"
    st.session_state.user_input = ""

# Filter selections
st.session_state.brand = st.sidebar.selectbox("Select Brand / اختر العلامة التجارية", options=list(gsk_brands.keys()), index=0 if st.session_state.brand=="" else list(gsk_brands.keys()).index(st.session_state.brand))
st.session_state.segment = st.sidebar.selectbox("Select RACE Segment / اختر شريحة RACE", race_segments)
st.session_state.barrier = st.sidebar.multiselect("Select Doctor Barrier / اختر حاجز الطبيب", options=doctor_barriers, default=st.session_state.barrier)
st.session_state.objective = st.sidebar.selectbox("Select Objective / اختر الهدف", objectives)
st.session_state.specialty = st.sidebar.selectbox("Select Doctor Specialty / اختر تخصص الطبيب", specialties)
st.session_state.persona = st.sidebar.selectbox("Select HCP Persona / اختر شخصية الطبيب", personas)
response_length_options = ["Short", "Medium", "Long"]
response_tone_options = ["Formal", "Casual", "Friendly", "Persuasive"]
st.session_state.response_length = st.sidebar.selectbox("Select Response Length / اختر طول الرد", response_length_options, index=response_length_options.index(st.session_state.response_length))
st.session_state.response_tone = st.sidebar.selectbox("Select Response Tone / اختر نبرة الرد", response_tone_options, index=response_tone_options.index(st.session_state.response_tone))

interface_mode = st.sidebar.radio("Interface Mode / اختر واجهة", ["Chatbot", "Card Dashboard", "Flow Visualization"])

# --- Load brand image safely ---
if st.session_state.brand:
    image_path = gsk_brands_images.get(st.session_state.brand)
    try:
        if image_path.startswith("http"):
            response = requests.get(image_path)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(image_path)
        st.image(img, width=200)
    except Exception:
        st.warning(f"⚠️ Could not load image for {st.session_state.brand}. Using placeholder.")
        st.image("https://via.placeholder.com/200x100.png?text=No+Image", width=200)

# --- Reset / New Discussion Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Clear Chat / مسح المحادثة"):
        st.session_state.chat_history = []
with col2:
    if st.button("🆕 Start a New Discussion"):
        st.session_state.chat_history = []
        st.session_state.brand = ""
        st.session_state.segment = ""
        st.session_state.barrier = []
        st.session_state.objective = ""
        st.session_state.specialty = ""
        st.session_state.persona = ""
        st.session_state.response_length = "Medium"
        st.session_state.response_tone = "Formal"
        st.session_state.user_input = ""
        st.success("New discussion started! All selections have been reset.")

# --- Chat container ---
chat_container = st.container()
placeholder_text = "Type your message..." if st.session_state.language == "English" else "اكتب رسالتك..."
st.session_state.user_input = st.text_area(placeholder_text, key="user_input", height=80, value=st.session_state.user_input)

# --- APACT Highlight Function ---
def highlight_apact(text):
    colors = {
        "Acknowledge": "#FFDDC1",
        "Probing": "#FFFACD",
        "Answer": "#C1FFD7",
        "Confirm": "#D1D1FF",
        "Transition": "#FFD1DC"
    }
    for step, color in colors.items():
        text = re.sub(
            fr"({step}:.*?)(?=(Acknowledge|Probing|Answer|Confirm|Transition|$))",
            lambda m: f"<div style='background:{color}; padding:8px; border-radius:6px; margin:5px 0;'>{m.group(1)}</div>",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )
    return text

# --- Create Word file function ---
def create_word_file(text, filename="AI_Response.docx"):
    doc = Document()
    doc.add_heading("AI Sales Call Assistant Response", level=1)
    for line in text.split("\n"):
        doc.add_paragraph(line)
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# --- Send button with APACT integration ---
if st.button("🚀 Send / أرسل") and st.session_state.user_input.strip():
    with st.spinner("Generating AI response... / جارٍ إنشاء الرد"):
        st.session_state.chat_history.append({"role": "user", "content": st.session_state.user_input})

        approaches_str = "\n".join(gsk_approaches)
        flow_str = " → ".join(sales_call_flow)

        prompt = f"""
Language: {st.session_state.language}
You are an expert GSK sales assistant. 
User input: {st.session_state.user_input}
RACE Segment: {st.session_state.segment}
Doctor Barrier: {', '.join(st.session_state.barrier) if st.session_state.barrier else 'None'}
Objective: {st.session_state.objective}
Brand: {st.session_state.brand}
Doctor Specialty: {st.session_state.specialty}
HCP Persona: {st.session_state.persona}
Approved GSK Sales Approaches:
{approaches_str}
Sales Call Flow Steps:
{flow_str}

Instructions for AI:
- Handle all objections using APACT (Acknowledge → Probing → Answer → Confirm → Transition).
- Clearly label each step.
- Tailor responses to persona, tone ({st.session_state.response_tone}), and length ({st.session_state.response_length}).
"""

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": f"You are a helpful sales assistant chatbot that responds in {st.session_state.language}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        ai_output = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "ai", "content": ai_output})
        st.session_state.user_input = ""  # reset input box after send

# --- Display chat history ---
with chat_container:
    if interface_mode == "Chatbot":
        st.subheader("💬 Chatbot Interface")
        for idx, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(
                    f"<div style='text-align:right; background:#d1e7dd; padding:10px; "
                    f"border-radius:12px; margin:10px 0;'>{msg['content']}</div>",
                    unsafe_allow_html=True
                )
            else:
                highlighted = highlight_apact(msg["content"])
                st.markdown(highlighted, unsafe_allow_html=True)

                # --- Download Button ---
                word_file = create_word_file(msg["content"])
                st.download_button(
                    label="📄 Download Response as Word",
                    data=word_file,
                    file_name=f"AI_Response_{idx}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"download_{idx}"
                )

    elif interface_mode == "Card Dashboard":
        st.subheader("📊 Card-Based Dashboard")
        segments_list = ["Evidence-Seeker", "Skeptic", "Time-Pressured"]
        for seg in segments_list:
            with st.expander(f"{seg} Segment"):
                st.write(f"Suggested approach for {seg} with {', '.join(st.session_state.barrier) if st.session_state.barrier else 'None'} barriers selected.")
                st.progress(70)
                st.button(f"Next Suggestion for {seg}")

    elif interface_mode == "Flow Visualization":
        st.subheader("🔗 HCP Engagement Flow")
        html_content = f"""
        <div style='font-family:sans-serif; background:#f0f2f6; padding:20px; border-radius:10px;'>
            <h3>{st.session_state.persona} Segment</h3>
            <p><b>Behavior:</b> {', '.join(st.session_state.barrier) if st.session_state.barrier else 'None'}</p>
            <p><b>Brand:</b> {st.session_state.brand}</p>
            <p><b>Sales Flow:</b> {" → ".join(sales_call_flow)}</p>
            <p><b>Tone:</b> {st.session_state.response_tone}</p>
            <p><b>AI Suggestion:</b> APACT objection handling phrasing generated by AI here...</p>
        </div>
        """
        components.html(html_content, height=300)

# --- Brand leaflet ---
if st.session_state.brand:
    st.markdown(f"[Brand Leaflet - {st.session_state.brand}]({gsk_brands[st.session_state.brand]})")
