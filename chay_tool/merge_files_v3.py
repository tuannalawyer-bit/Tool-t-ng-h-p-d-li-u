import pandas as pd
import sys
import io
import re
from rapidfuzz import fuzz, process
from unidecode import unidecode
from slugify import slugify

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize_address(s):
    if pd.isna(s):
        return ""
    s = str(s).lower()
    s = unidecode(s)                 # Remove Vietnamese accents
    s = re.sub(r'[\W_]+', ' ', s)    # Replace non-alphanumeric with spaces
    s = " ".join(s.split())          # Remove extra spaces
    return s

def main():
    path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
    path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"
    output_path = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\merged_result_v80.xlsx"

    print(f"Loading {path1}...")
    df1 = pd.read_excel(path1)
    
    print(f"Loading {path2}...")
    df2 = pd.read_excel(path2, header=2)

    # Filter out empty rows if any
    df1 = df1.dropna(subset=['Địa chỉ'])
    df2 = df2.dropna(subset=['Thông tin MB đang thuê'])

    print("Normalizing addresses...")
    df1['addr_clean'] = df1['Địa chỉ'].apply(normalize_address)
    df2['addr_clean'] = df2['Thông tin MB đang thuê'].apply(normalize_address)

    print("Performing fuzzy match (Threshold: 80%)...")
    # We will try to match each row in df1 with the best matching row in df2
    df2_addresses = df2['addr_clean'].tolist()
    
    matches = []
    threshold = 80  # Similarity threshold
    
    for idx1, addr1 in enumerate(df1['addr_clean']):
        if not addr1:
            matches.append(None)
            continue
            
        best_match = process.extractOne(addr1, df2_addresses, scorer=fuzz.token_sort_ratio)
        
        if best_match and best_match[1] >= threshold:
            # best_match is (value, score, index_in_df2_addresses)
            matches.append(best_match[2])
        else:
            matches.append(None)

    # Create a column for matched index
    df1['df2_idx'] = matches

    # Merge
    # We'll do a left join from df1 to df2 based on the matched index
    merged_df = df1.merge(df2, left_on='df2_idx', right_index=True, how='left', suffixes=('_file1', '_file2'))

    # Drop helper columns
    merged_df = merged_df.drop(columns=['addr_clean_file1', 'addr_clean_file2', 'df2_idx'], errors='ignore')

    print(f"Saving result to {output_path}...")
    merged_df.to_excel(output_path, index=False)
    print("Done!")

if __name__ == "__main__":
    main()
