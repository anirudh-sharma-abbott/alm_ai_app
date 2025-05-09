# FRS Requirement Classification Dashboard

This Streamlit-based application analyzes and reclassifies Functional Requirements Specifications (FRS) within a regulated Veeva Medical CRM environment. It flags misclassified entries based on domain-specific logic and offers a GPT-powered assistant to reword requirement descriptions for clarity and compliance.

---

## Features

### 1. Requirement Reclassification
- Reclassifies requirements based on predefined keyword logic.
- Flags mismatches between manual classification and keyword-based inference.
- Allows download of filtered misclassifications by folder.

### 2. Summary & Insights
- Displays misclassification trends over time (monthly view).
- Shows cycle-level and folder-level misclassification counts.
- Pie charts showing % distribution across Target Cycles and Folders.
- Highlights future-dated requirements for audit/investigation.

### 3. GPT-Powered Rewriter
- Uses OpenAI GPT-3.5 Turbo to reword requirement descriptions.
- Applies a regulatory-aware system prompt aligned with Medical CRM documentation standards.
- Ensures language is clear and professional without altering business intent.

---

## How to Use

1. Clone the Repository

git clone https://github.com/<your-org>/frs-dashboard.git
cd frs-dashboard

2. Set Up Environment
Create a .env file in the root directory:
OPENAI_API_KEY=your_openai_key_here

3. Install Dependencies
pip install -r requirements.txt

4. Launch the Streamlit App
streamlit run main.py

5. Upload Your Input File
Upload an Excel file (.xlsx) with the following columns:

Required Columns
FRS Req ID
FRS Name
Folder Name
Description
Requirement Classification
Creation Date
Target Cycle (optional)

Reclassification Logic
Requirements are reclassified as:

2 - Quality Non-Critical (QNC) if they include keywords like "sample", "lot number", "product", etc.

Otherwise, they are inferred as 5 - Non-Regulated.

If the manual classification does not match the inferred class, the requirement is marked as misclassified.

GPT Rewriting Prompt (System Message)
You are an expert in regulatory-compliant Veeva Medical CRM documentation. Reword the given requirement for clarity and precision without changing the business logic or intent.
The model rewrites the requirement while maintaining its original business meaning, tailored to medical documentation standards.

Visualization Examples
Bar charts: Misclassified requirements per folder or target cycle

Line charts: Monthly misclassification trends

Pie charts: Distribution of all requirements by cycle and folder

Table: Requirements with future-dated creation timestamps