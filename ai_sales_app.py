
import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openai import OpenAI

api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("Enter your OpenAI API key", type="password")
if api_key:
    client = OpenAI(api_key=api_key)

@st.cache_data
def load_data():
    survey_df = pd.read_excel("segmentation survey.xlsx")
    actions_df = pd.read_excel("Shingrix RACE segmentation actions.xlsx")

    actions_cleaned = actions_df[['RACE', 'Description', 'Limitation / Barriers to expand', 'Proposed Action']].dropna(subset=['RACE'])
    actions_cleaned = actions_cleaned.drop_duplicates(subset=['RACE'])

    hcp_race = survey_df[['Account', 'RACE']].drop_duplicates()
    recommendations = pd.merge(hcp_race, actions_cleaned, on='RACE', how='left')
    return recommendations

recommendations = load_data()

st.title("AI Sales Call Assistant for Pharma Reps")

search_name = st.text_input("Search for HCP Name")
filtered = recommendations[recommendations['Account'].str.contains(search_name, case=False)] if search_name else recommendations

if not filtered.empty:
    hcp_name = st.selectbox("Select HCP", sorted(filtered['Account'].unique()))
    hcp_data = filtered[filtered['Account'] == hcp_name].iloc[0]

    st.subheader("HCP Profile & Recommendations")
    st.markdown(f"**Segment (RACE):** {hcp_data['RACE']}")
    st.markdown(f"**Description:** {hcp_data['Description']}")
    st.markdown(f"**Main Barrier:** {hcp_data['Limitation / Barriers to expand']}")
    st.markdown(f"**Recommended Action:** {hcp_data['Proposed Action']}")

    notes = st.text_area("Add your notes for this HCP")

    objection = st.text_input("Doctor Objection / Question")
    if objection and api_key:
        with st.spinner("Generating smart response..."):
            chat_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a pharma sales expert. Help a rep respond to this doctor objection, considering the barrier: '{hcp_data['Limitation / Barriers to expand']}'."},
                    {"role": "user", "content": objection}
                ]
            )
            response_text = chat_response.choices[0].message.content
            st.success("Suggested Reply:")
            st.write(response_text)

    def generate_pdf(hcp_data, notes):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("HCP Sales Call Recommendation", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"HCP Name: {hcp_data['Account']}", styles['Normal']))
        story.append(Paragraph(f"Segment (RACE): {hcp_data['RACE']}", styles['Normal']))
        story.append(Paragraph(f"Description: {hcp_data['Description']}", styles['Normal']))
        story.append(Paragraph(f"Main Barrier: {hcp_data['Limitation / Barriers to expand']}", styles['Normal']))
        story.append(Paragraph(f"Recommended Action: {hcp_data['Proposed Action']}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Rep Notes:", styles['Heading3']))
        story.append(Paragraph(notes if notes else "No notes provided.", styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer

    if st.button("Download as PDF"):
        pdf_buffer = generate_pdf(hcp_data, notes)
        st.download_button(label="Download PDF", data=pdf_buffer, file_name=f"{hcp_data['Account']}_recommendation.pdf", mime="application/pdf")
else:
    st.warning("No matching HCPs found.")
