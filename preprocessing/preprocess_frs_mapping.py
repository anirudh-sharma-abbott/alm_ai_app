import pandas as pd

# File paths
frs_file = "../data/Requirements_ALM.xlsx"
urs_file = "../data/URS_Folder_ALM.xlsx"
output_file = "../outputs/frs_to_folder_mapping.xlsx"

# Load Excel files
frs_df = pd.read_excel(frs_file)
urs_df = pd.read_excel(urs_file)

# Step 1: Filter only FRS-type requirements
frs_only = frs_df[frs_df['Name'].str.startswith("FRS.")].copy()

# Step 2: Merge FRS → URS using 'Req Parent'
merged = frs_only.merge(
    urs_df[['Name', 'Req Parent']],
    left_on='Req Parent',
    right_on='Name',
    suffixes=('_FRS', '_URS')
)

# Debug: Show all available columns
print("Merged columns:", merged.columns.tolist())

# Step 3: Rename columns
merged = merged.rename(columns={
    'Req ID': 'FRS Req ID',
    'Name_FRS': 'FRS Name',
    'Name_URS': 'URS ID',
    'Req Parent_URS': 'Folder Name'
})

# Step 4: Select and reorder final columns
output_df = merged[[ 
    'FRS Req ID',
    'FRS Name',
    'URS ID',
    'Folder Name',
    'Description',
    'Requirement Classification',
    'Regulatory Risk',
    'Creation Date',
    'Target Cycle'
]].copy()

# Step 5: Preview result
print(output_df.head())

# Step 6: Save to Excel
output_df.to_excel(output_file, index=False)
print(f"Mapping complete. File saved to {output_file}")
