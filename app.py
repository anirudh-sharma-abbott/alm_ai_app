import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import plotly.express as px

# Load environment variables and OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Requirement Cluster Review", layout="wide")
st.title("FRS Requirement Classification Review")

# Upload Excel
uploaded_file = st.sidebar.file_uploader("Upload Final Mapping File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # --- Add logical reclassification based on keywords ---
    qnc_keywords = ["sample", "samples", "sampled report", "lot number", "expiration date", "signature", "product", "products"]

    def classify(desc):
        if pd.isna(desc): return "5 - Non-Regulated"
        desc = desc.lower()
        for kw in qnc_keywords:
            if re.search(rf"\b{re.escape(kw)}\b", desc):
                return "2 - Quality Non-Critical (QNC)"
        return "5 - Non-Regulated"

    df["Reclassified"] = df["Description"].apply(classify)

    # --- Flag mismatches ---
    df["Misclassified"] = (
        (df["Requirement Classification"] == "2 - Quality Non-Critical (QNC)") &
        (df["Reclassified"] == "5 - Non-Regulated")
    )

    # --- Folder cluster view ---
    folders = df["Folder Name"].dropna().unique()
    st.sidebar.markdown("### Choose Folder")
    selected_folder = st.sidebar.selectbox("Select Folder", folders)

    filtered = df[(df["Folder Name"] == selected_folder) & (df["Misclassified"])]

    st.subheader(f"🔍 Misclassified Requirements in Folder: {selected_folder}")
    st.write("These are requirements currently labeled QNC but should be Non-Regulated based on the description.")
    st.dataframe(filtered[["FRS Req ID", "FRS Name", "Requirement Classification", "Reclassified", "Description"]])

    # --- Export filtered ---
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Misclassifications",
        data=csv,
        file_name=f"misclassified_{selected_folder}.csv",
        mime='text/csv'
    )

    # --- Summary Table + Visualization ---
    st.markdown("---")
    st.header("Folder-Level Misclassification Summary")
    summary = df[df["Misclassified"]].groupby("Folder Name").size().reset_index(name="Misclassified Count")
    st.dataframe(summary)

    fig = px.bar(summary, x="Folder Name", y="Misclassified Count", title="Misclassified Requirements per Folder",
                 labels={"Folder Name": "Folder", "Misclassified Count": "Count"})
    st.plotly_chart(fig, use_container_width=True)

    # --- GPT-based rewording ---
    st.markdown("---")
    st.header("GPT Rewording")
    req_ids = df["FRS Req ID"].dropna().unique()
    selected_id = st.selectbox("Select FRS Req ID", req_ids)
    orig_text = df[df["FRS Req ID"] == selected_id]["Description"].values[0]

    st.text_area("Original Description", orig_text, height=150)

    if st.button("Reword Description"):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Reword this requirement for clarity:\n{orig_text}"}]
            )
            reworded = response.choices[0].message.content
            st.success("Reworded Output")
            st.text_area("GPT Reworded", value=reworded, height=150)
        except Exception as e:
            st.error(f"Error calling OpenAI: {e}")