import pandas as pd
import sys
import io

# Fix printing encoding issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

file_path = r"d:\Dự án AI\map Ch\danh sach CH.xlsx"
try:
    df = pd.read_excel(file_path, nrows=5)
    print("--- Top 5 Rows ---")
    print(df)
    
    df_all = pd.read_excel(file_path)
    print("\n--- Info ---")
    print(f"Total rows: {len(df_all)}")
    print(f"Columns: {df_all.columns.tolist()}")
    
    # Print types and null counts
    print(df_all.dtypes)
    print(df_all.isnull().sum())
except Exception as e:
    print(f"Error reading file: {e}")
