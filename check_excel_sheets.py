

import pandas as pd

excel_file = 'Gen_AI Dataset.xlsx'

print("="*70)
print(f"Checking sheets in: {excel_file}")
print("="*70)

# Read all sheet names
excel_data = pd.ExcelFile(excel_file)
sheet_names = excel_data.sheet_names

print(f"\nFound {len(sheet_names)} sheets:")
for i, name in enumerate(sheet_names, 1):
    print(f"  {i}. '{name}'")

# Show preview of each sheet
print("\n" + "="*70)
print("SHEET PREVIEWS")
print("="*70)

for sheet_name in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(f"\n📋 Sheet: '{sheet_name}'")
    print(f"   Rows: {len(df)}")
    pArint(f"   Columns: {list(df.columns)}")
    print(f"   First row sample:")
    if len(df) > 0:
        print(f"   {df.iloc[0].to_dict()}")

print("\n" + "="*70)
print("✓ Analysis complete!")
print("="*70)
print("\nNow update evaluation_script.py with the correct sheet names.")