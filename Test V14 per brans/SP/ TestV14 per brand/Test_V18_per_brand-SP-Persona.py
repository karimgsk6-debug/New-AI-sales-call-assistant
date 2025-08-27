import streamlit as st
from PIL import Image
import requests
from io import BytesIO, BytesIO as io_bytes
import groq
from groq import Groq
from datetime import datetime
import pandas as pd
import altair as alt

# --- Optional Word download ---
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    st.warning("⚠️ python-docx not installed. Word download unavailable.")

# --- Optional matplotlib for charts ---
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    st.info("⚠️ matplotlib not installed. Charts will fallback to Altair.")

# --- Groq client ---
client = Groq(api_key="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")

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Language ---
language = st.radio("Select Language / اختر اللغة", options=["English", "العربية"])

# --- GSK Logo ---
logo_url = "https://www.tungsten-network.com/wp-content/uploads/2020/05/GSK_Logo_Full_Colour_RGB.png"
st.image(logo_url, width=150)
st.title("🧠 AI Sales Call Assistant")

# --- Sidebar Filters ---
brand = st.sidebar.selectbox("Select Brand", ["Shingrix", "Trelegy", "Zejula"])
segment = st.sidebar.selectbox("Select RACE Segment", ["R", "A", "C", "E"])
barrier = st.sidebar.multiselect("Select Doctor Barrier", ["No time", "Cost", "Not convinced"])
objective = st.sidebar.selectbox("Select Objective", ["Awareness", "Adoption", "Retention"])
specialty = st.sidebar.selectbox("Select Specialty", ["GP", "Cardiologist"])
persona = st.sidebar.selectbox("Select Persona", ["Uncommitted Vaccinator", "Reluctant Efficiency"])
response_length = st.sidebar.selectbox("Response Length", ["Short", "Medium", "Long"])
response_tone = st.sidebar.selectbox("Response Tone", ["Formal", "Friendly", "Persuasive"])

# --- Clear chat ---
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []

# --- Display chat ---
chat_placeholder = st.empty()

def display_chat():
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")
            # Handle chart instructions
            if "generate_chart:" in msg["content"]:
                chart_type = msg["content"].split("generate_chart:")[-1].strip()

                # Patient Profile Chart (bar)
                if chart_type == "patient_profile":
                    data = pd.DataFrame({
                        "Parameter": ["Age", "Comorbidity", "Risk Level"],
                        "Value": [65, 2, 8]
                    })
                    fig = alt.Chart(data).mark_bar().encode(
                        x='Parameter',
                        y='Value',
                        color='Parameter'
                    )
                    st.altair_chart(fig, use_container_width=True)

                # Medical Trend Chart (line)
                elif chart_type == "medical_trend":
                    df = pd.DataFrame({
                        "Month": ["Jan", "Feb", "Mar", "Apr"],
                        "Visits": [10, 15, 13, 20]
                    })
                    if MATPLOTLIB_AVAILABLE:
                        fig, ax = plt.subplots()
                        ax.plot(df["Month"], df["Visits"], marker='o')
                        ax.set_title("Medical Visits Trend")
                        ax.set_xlabel("Month")
                        ax.set_ylabel("Number of Visits")
                        st.pyplot(fig)
                    else:
                        # fallback to Altair line chart
                        line_chart = alt.Chart(df).mark_line(point=True).encode(
                            x='Month',
                            y='Visits'
                        )
                        st.altair_chart(line_chart, use_container_width=True)

display_chat()

# --- Chat input ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message...", key="user_input_box")
    submitted = st.form_submit_button("➤")

if submitted and user_input.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_input, "time": datetime.now().strftime("%H:%M")})
    
    prompt = f"""
Language: {language}
User input: {user_input}
Brand: {brand}
Persona: {persona}
Segment: {segment}
Doctor Barriers: {', '.join(barrier)}
Objective: {objective}
Response Tone: {response_tone}
Instructions: Suggest visuals (charts, patient profile, medical trends) using 'generate_chart:<type>'.
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "system", "content": f"You are a sales assistant in {language}."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )
    ai_output = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "ai", "content": ai_output, "time": datetime.now().strftime("%H:%M")})
    
    display_chat()

# --- Word download ---
if DOCX_AVAILABLE and st.session_state.chat_history:
    latest_ai = [msg["content"] for msg in st.session_state.chat_history if msg["role"] == "ai"]
    if latest_ai:
        doc = Document()
        doc.add_heading("AI Sales Call Response", 0)
        doc.add_paragraph(latest_ai[-1])
        word_buffer = io_bytes()
        doc.save(word_buffer)
        st.download_button("📥 Download as Word (.docx)", word_buffer.getvalue(), file_name="AI_Response.docx")
