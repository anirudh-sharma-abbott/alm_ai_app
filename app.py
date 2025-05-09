import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import plotly.express as px
from datetime import datetime

# Load environment variables and OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Requirement Cluster Review", layout="wide")
st.title("FRS Requirement Classification Dashboard")

# File upload
uploaded_file = st.sidebar.file_uploader("Upload Final Mapping File", type=["xlsx"])
page = st.sidebar.radio("Select View", ["Reclassification", "Summary & Insights", "GPT Rewriter"])

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

    if "Creation Date" in df.columns:
        df["Creation Date"] = pd.to_datetime(df["Creation Date"], errors="coerce")

    # --------------------------
    # SECTION: Reclassification View
    # --------------------------
    if page == "Reclassification":
        folders = df["Folder Name"].dropna().unique()
        selected_folder = st.selectbox("Select Folder", folders)

        filtered = df[(df["Folder Name"] == selected_folder) & (df["Misclassified"])]
        st.subheader(f"Misclassified Requirements in Folder: {selected_folder}")
        st.caption("These are currently labeled QNC but inferred as Non-Regulated based on keyword match.")
        st.dataframe(filtered[["FRS Req ID", "FRS Name", "Requirement Classification", "Reclassified", "Description"]])

        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button("Download Misclassifications", csv, f"misclassified_{selected_folder}.csv", "text/csv")

    # --------------------------
    # SECTION: Summary & Insights
    # --------------------------
    elif page == "Summary & Insights":
        st.header("Folder-Level Misclassification Summary")
        summary = df[df["Misclassified"]].groupby("Folder Name").size().reset_index(name="Misclassified Count")
        st.dataframe(summary)
        fig = px.bar(summary, x="Folder Name", y="Misclassified Count", title="Misclassified Requirements per Folder")
        st.plotly_chart(fig, use_container_width=True)

        if "Creation Date" in df.columns:
            st.header("Misclassification Trend Over Time")
            today = pd.to_datetime(datetime.today())
            trend_df = df[(df["Misclassified"]) & (df["Creation Date"].notna()) & (df["Creation Date"] <= today)]

            if (df["Creation Date"] > today).any():
                future_df = df[df["Creation Date"] > today]
                st.warning(f"{len(future_df)} requirements have a Creation Date in the future.")
                with st.expander("View Future-Dated Requirements"):
                    st.dataframe(future_df[["FRS Req ID", "FRS Name", "Creation Date", "Folder Name"]])

            trend = trend_df.groupby(trend_df["Creation Date"].dt.to_period("M")).size()
            trend.index = trend.index.to_timestamp()
            fig2 = px.line(trend, title="Misclassification Trend by Month", labels={"value": "Count", "index": "Month"})
            st.plotly_chart(fig2, use_container_width=True)

        if "Target Cycle" in df.columns:
            st.header("Target Cycle Summary")
            cycle_summary = df.groupby("Target Cycle").agg({
                "FRS Req ID": "count",
                "Misclassified": "sum"
            }).reset_index().rename(columns={"FRS Req ID": "Total Reqs", "Misclassified": "Misclassified Count"})
            st.dataframe(cycle_summary)
            fig3 = px.bar(cycle_summary, x="Target Cycle", y="Misclassified Count", title="Misclassifications by Target Cycle")
            st.plotly_chart(fig3, use_container_width=True)

        st.header("Requirement Distribution by Category")
        if "Target Cycle" in df.columns:
            fig_cycle = px.pie(df, names='Target Cycle', title='Requirement Distribution by Target Cycle')
            st.plotly_chart(fig_cycle, use_container_width=True)
        fig_folder = px.pie(df, names='Folder Name', title='Requirement Distribution by Folder')
        st.plotly_chart(fig_folder, use_container_width=True)

        if "Creation Date" in df.columns and "Folder Name" in df.columns:
            df['Month'] = df["Creation Date"].dt.to_period('M').astype(str)
            folder_trend_df = df[df["Creation Date"] <= datetime.today()]
            folder_trend_df["Month"] = folder_trend_df["Creation Date"].dt.to_period("M").astype(str)

            folder_trend = folder_trend_df.groupby(["Month", "Folder Name"]).size().reset_index(name="Count")
            fig_trend = px.line(folder_trend, x='Month', y='Count', color='Folder Name',
                                title='Requirement Submission Trend by Folder')
            st.plotly_chart(fig_trend, use_container_width=True)

    # --------------------------
    # SECTION: GPT Rewriter
    # --------------------------
    elif page == "GPT Rewriter":
        st.header("Requirement Rewording Assistant")

        req_ids = df["FRS Req ID"].dropna().unique()
        selected_id = st.selectbox("Select FRS Req ID", req_ids)
        orig_text = df[df["FRS Req ID"] == selected_id]["Description"].values[0]
        st.text_area("Original Description", orig_text, height=150)

        if st.button("Reword with GPT"):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert in regulatory-compliant Veeva Medical CRM documentation. Reword the given requirement for clarity and precision without changing the business logic or intent."
                        },
                        {
                            "role": "user",
                            "content": f"Reword this Medical CRM requirement for clarity:\n{orig_text}"
                        }
                    ]
                )
                reworded = response.choices[0].message.content
                st.success("Reworded Output")
                st.text_area("Reworded Description", value=reworded, height=150)
            except Exception as e:
                st.error(f"Error calling OpenAI: {e}")
