import streamlit as st
import os
from groq import Groq

# Initialize Groq client with your API key
client = Groq(api_key="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",)

# ... [Keep all previous definitions: gsk_brands, brand_images, gsk_approaches, translations] ...

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

        # Chatbot-style card for AI output
        st.subheader(t["result_title"])
        st.markdown(
            f"""
            <div style="
                background-color:#f0f2f6;
                padding:15px;
                border-radius:12px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                max-height:300px;
                overflow-y:auto;
                font-family:sans-serif;
                white-space:pre-wrap;
            ">
            {ai_output}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Add PIL link
        st.markdown(f"[{t['leaflet']} - {brand}]({gsk_brands[brand]})")
