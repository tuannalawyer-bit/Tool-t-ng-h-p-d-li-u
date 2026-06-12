import pandas as pd
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

file_path = r"d:\Dự án AI\map Ch\danh sach CH.xlsx"
df = pd.read_excel(file_path)

print("Checking coordinate conversions:")
for col in ['Vĩ độ', 'Kinh độ']:
    print(f"\nAnalyzing column: {col}")
    # Check non-numeric values
    non_numeric = df[pd.to_numeric(df[col], errors='coerce').isna()]
    print(f"Number of non-numeric rows in {col}: {len(non_numeric)}")
    if len(non_numeric) > 0:
        print("Sample non-numeric values:")
        print(non_numeric[[col]].head(10))
        
print("\nRange of values if converted to numeric:")
df_clean = df.copy()
df_clean['lat'] = pd.to_numeric(df_clean['Vĩ độ'], errors='coerce')
df_clean['lon'] = pd.to_numeric(df_clean['Kinh độ'], errors='coerce')
print(df_clean[['lat', 'lon']].describe())
