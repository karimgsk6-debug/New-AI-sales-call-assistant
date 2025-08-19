import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Sales Call Assistant", layout="wide", page_icon="🧠")

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters & Options")

# HCP Persona & Behavior
persona = st.sidebar.selectbox("HCP Persona", ["Evidence-Seeker", "Skeptic", "Time-Pressured"])
behavior = st.sidebar.multiselect("Behavior", ["Scientific", "Analytical", "Friendly"])
brand = st.sidebar.selectbox("Brand", ["Brand A", "Brand B", "Brand C"])

# Tone & Response Length
tone = st.sidebar.radio("Tone", ["Formal", "Casual"])
length = st.sidebar.radio("Response Length", ["Short", "Long"])

# Interface Mode
interface_mode = st.sidebar.radio("Interface Mode", ["Chatbot", "Card Dashboard", "Flow Visualization"])

# -------------------------------
# User Input
# -------------------------------
st.title("🧠 AI Sales Call Assistant")
user_input = st.text_input("Type your question or scenario:")

if st.button("Get AI Suggestion"):
    ai_response = f"AI ({persona}, {', '.join(behavior)}, {brand}, {tone}, {length}):\nThis is a tailored suggestion for your scenario."
    
    # -------------------------------
    # 1. Chatbot Interface
    # -------------------------------
    if interface_mode == "Chatbot":
        st.subheader("💬 Chatbot Interface")
        st.info(ai_response)
    
    # -------------------------------
    # 2. Card-Based Dashboard
    # -------------------------------
    elif interface_mode == "Card Dashboard":
        st.subheader("📊 Card-Based Dashboard")
        segments = ["Evidence-Seeker", "Skeptic", "Time-Pressured"]
        for seg in segments:
            with st.expander(f"{seg} Segment"):
                st.write(f"Suggested approach for {seg} with {', '.join(behavior)} behavior.")
                st.progress(70)  # Example confidence
                st.button(f"Next Suggestion for {seg}")
    
    # -------------------------------
    # 3. Flow Visualization
    # -------------------------------
    elif interface_mode == "Flow Visualization":
        st.subheader("🔗 HCP Engagement Flow")
        html_content = f"""
        <div style='font-family:sans-serif; background:#f0f2f6; padding:20px; border-radius:10px;'>
            <h3>{persona} Segment</h3>
            <p><b>Behavior:</b> {', '.join(behavior)}</p>
            <p><b>Brand:</b> {brand}</p>
            <p><b>Tone:</b> {tone}</p>
            <p><b>AI Suggestion:</b> Example probing question or approach here...</p>
        </div>
        """
        components.html(html_content, height=250)

# -------------------------------
# Optional Footer
# -------------------------------
st.markdown("---")
st.markdown("Developed for Pharma Sales Reps | Interactive AI Guidance")
