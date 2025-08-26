import streamlit as st
from PIL import Image
from io import BytesIO
import groq
from groq import Groq
from datetime import datetime
import os

# --- Word export ---
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    st.warning("⚠️ python-docx not installed. Word download unavailable.")

# --- Initialize Groq client ---
client = Groq(api_key="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")  # Add your Groq API key here

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Language ---
language = st.radio("Select Language / اختر اللغة", options=["English", "العربية"])

# --- GSK Logo ---
logo_fallback_url = "https://www.tungsten-network.com/wp-content/uploads/2020/05/GSK_Logo_Full_Colour_RGB.png"
col1, col2 = st.columns([1,5])
with col1:
    st.image(logo_fallback_url, width=120)
with col2:
    st.title("🧠 AI Sales Call Assistant")

# --- Brand assets ---
gsk_brands = ["Shingrix", "Trelegy", "Zejula"]
brand_pdfs = {
    "Shingrix": "assets/PDFs/Shingrix.pdf",
    "Trelegy": "assets/PDFs/Trelegy.pdf",
    "Zejula": "assets/PDFs/Zejula.pdf",
}
brand_visuals = {
    "Shingrix": "assets/Images/Shingrix_chart.png",
    "Trelegy": "assets/Images/Trelegy_diagram.png",
    "Zejula": "assets/Images/Zejula_flow.png",
}

# --- Filters ---
race_segments = ["R – Reach", "A – Acquisition", "C – Conversion", "E – Engagement"]
doctor_barriers = ["HCP does not consider HZ as risk","No time to discuss preventive measures",
                   "Cost considerations","Not convinced HZ Vx effective","Accessibility issues"]
objectives = ["Awareness", "Adoption", "Retention"]
specialties = ["GP", "Cardiologist", "Dermatologist", "Endocrinologist", "Pulmonologist"]
personas = ["Uncommitted Vaccinator","Reluctant Efficiency","Patient Influenced","Committed Vaccinator"]
gsk_approaches = ["Use data-driven evidence","Focus on patient outcomes","Leverage storytelling techniques"]
sales_call_flow = ["Prepare","Engage","Create Opportunities","Influence","Drive Impact","Post Call Analysis"]

# --- Sidebar ---
st.sidebar.header("Filters & Options")
brand = st.sidebar.selectbox("Select Brand", options=gsk_brands)
segment = st.sidebar.selectbox("Select RACE Segment", race_segments)
barrier = st.sidebar.multiselect("Select Doctor Barrier", doctor_barriers)
objective = st.sidebar.selectbox("Select Objective", objectives)
specialty = st.sidebar.selectbox("Select Doctor Specialty", specialties)
persona = st.sidebar.selectbox("Select HCP Persona", personas)
response_length = st.sidebar.selectbox("Response Length", ["Short", "Medium", "Long"])
response_tone = st.sidebar.selectbox("Response Tone", ["Formal", "Casual", "Friendly", "Persuasive"])

# --- Clear chat ---
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []

# --- Chat display ---
st.subheader("💬 Chatbot Interface")
chat_placeholder = st.empty()

def display_chat():
    chat_html = ""
    for msg in st.session_state.chat_history:
        time = msg.get("time","")
        content = msg["content"].replace("\n","<br>")
        # Bold APACT steps
        apact_steps = ["Acknowledge","Probing","Answer","Confirm","Transition"]
        for step in apact_steps:
            content = content.replace(step,f"<b>{step}</b><br>")
        if msg["role"]=="user":
            chat_html += f"<div style='text-align:right;background:#dcf8c6;padding:10px;border-radius:15px;margin:5px;display:inline-block;max-width:80%'>{content}<br><span style='font-size:10px;color:gray;'>{time}</span></div>"
        else:
            chat_html += f"<div style='text-align:left;background:#f0f2f6;padding:10px;border-radius:15px;margin:5px;display:inline-block;max-width:80%'>{content}<br><span style='font-size:10px;color:gray;'>{time}</span></div>"
    chat_placeholder.markdown(chat_html, unsafe_allow_html=True)

display_chat()

# --- Chat input ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message...")
    submitted = st.form_submit_button("➤")

if submitted and user_input.strip():
    st.session_state.chat_history.append({"role":"user","content":user_input,"time":datetime.now().strftime("%H:%M")})

    approaches_str = "\n".join(gsk_approaches)
    flow_str = " → ".join(sales_call_flow)

    prompt = f"""
Language: {language}
User input: {user_input}
RACE Segment: {segment}
Doctor Barrier: {', '.join(barrier) if barrier else 'None'}
Objective: {objective}
Brand: {brand}
Doctor Specialty: {specialty}
HCP Persona: {persona}
Approved Sales Approaches:
{approaches_str}
Sales Call Flow Steps:
{flow_str}
Use APACT (Acknowledge → Probing → Answer → Confirm → Transition) technique for handling objections.
Refer to PDF: {brand_pdfs[brand]}
Use visual guide: {brand_visuals[brand]}
Response Length: {response_length}
Response Tone: {response_tone}
Provide actionable suggestions tailored to this persona in a friendly and professional manner.
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"system","content":f"You are a helpful sales assistant chatbot in {language}."},
                  {"role":"user","content":prompt}],
        temperature=0.7
    )
    ai_output = response.choices[0].message.content
    st.session_state.chat_history.append({"role":"ai","content":ai_output,"time":datetime.now().strftime("%H:%M")})
    display_chat()

# --- PDF download & visual with existence check ---
if os.path.exists(brand_pdfs[brand]):
    with open(brand_pdfs[brand],"rb") as f:
        st.download_button(f"📄 Download {brand} PDF", data=f, file_name=f"{brand}.pdf")
else:
    st.warning(f"⚠️ PDF for {brand} not found.")

if os.path.exists(brand_visuals[brand]):
    try:
        img = Image.open(brand_visuals[brand])
        st.image(img, width=400, caption=f"{brand} Visual Guide")
    except:
        st.warning(f"⚠️ Could not load visual for {brand}.")
else:
    st.warning(f"⚠️ Visual for {brand} not found.")

# --- Word download ---
if DOCX_AVAILABLE and st.session_state.chat_history:
    latest_ai = [msg["content"] for msg in st.session_state.chat_history if msg["role"]=="ai"]
    if latest_ai:
        from io import BytesIO as io_bytes
        doc = Document()
        doc.add_heading("AI Sales Call Response",0)
        doc.add_paragraph(latest_ai[-1])
        word_buffer = io_bytes()
        doc.save(word_buffer)
        st.download_button("📥 Download as Word (.docx)", word_buffer.getvalue(), file_name="AI_Response.docx")
