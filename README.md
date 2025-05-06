# ALM Requirement Classification & Rewording App

This Streamlit-based tool helps teams analyze and improve Functional Requirement Specifications (FRS) from ALM by:

- Grouping requirements into clusters based on functional Folder Names
- Identifying misclassified requirements (e.g., incorrectly labeled as “2 - QNC” instead of “5 - Non-Regulated”)
- Enhancing requirement descriptions using GPT-powered rewording
- Visualizing folder-wise misclassification summaries
- Exporting CSV files of filtered results per folder

---

## Features

- Upload ALM FRS Mapping file (`frs_to_folder_mapping.xlsx`)
- Automatic reclassification based on keywords in descriptions:
  - Descriptions containing “sample,” “lot number,” “product,” etc., remain QNC
  - All others are suggested as Non-Regulated
- Clustered view based on `Folder Name`
- GPT-based rewording of requirement descriptions
- Export misclassified entries per folder
- Summary bar chart showing misclassification count by folder

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your OpenAI key in a .env file
echo "OPENAI_API_KEY=sk-xxxxx" > .env

# 3. Run the Streamlit app
streamlit run app.py
