import streamlit as st
import os
from groq import Groq

# Initialize Groq client with your API key
client = Groq(api_key="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",)

# ... [Keep previous definitions: gsk_brands, brand_images, gsk_approaches, translations] ...

# Load language dictionary
t = translations[language]

# UI
st.title(t["title"])
st.markdown(t["description"])

segment = st.selectbox(t["select_segment"], t["segments"])
behavior = st.selectbox(t["select_behavior"], t["behaviors"])
objective = st.selectbox(t["select_objective"], t["objectives"])
brand = st.selectbox(t["select_brand"], list(gsk_brands.keys()))

# Display brand image
if brand in brand_images:
    st.image(brand_images[brand], width=150)

# Show approved selling approaches
st.subheader(t["approved_approaches"])
for a in gsk_approaches:
    st.write(f"- {a}")

# Chat history container
chat_container = st.container()

# Generate AI suggestions
if st.button(t["generate"]):
    with st.spinner(t["loading"]):
        approaches_str = "\n".join(gsk_approaches)
        prompt = t["user_prompt"].format(
            segment=segment,
            behavior=behavior,
            objective=objective,
            brand=brand,
            approaches=approaches_str
        )

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": t["system_prompt"]},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        ai_output = response.choices[0].message.content

        # Display chat bubbles
        with chat_container:
            # User input bubble
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
                <strong>You:</strong><br>
                Segment: {segment}<br>
                Behavior: {behavior}<br>
                Objective: {objective}<br>
                Brand: {brand}
                </div>
                """,
                unsafe_allow_html=True
            )

            # AI response bubble
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
                <strong>AI:</strong><br>
                {ai_output}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Add PIL link below chat
        st.markdown(f"[{t['leaflet']} - {brand}]({gsk_brands[brand]})")
