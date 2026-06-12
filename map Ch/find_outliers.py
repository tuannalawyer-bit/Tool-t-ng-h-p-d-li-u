import pandas as pd
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

file_path = r"d:\Dự án AI\map Ch\danh sach CH.xlsx"
df = pd.read_excel(file_path)

# Convert after replacing , and cleaning strings
def clean_coord(val):
    if pd.isna(val):
        return None
    s = str(val).strip().replace(',', '.')
    # If multiple dots due to replacement or original typo
    if s.count('.') > 1:
        # keep only first dot? or just let it fail and handle it
        parts = s.split('.')
        s = parts[0] + '.' + "".join(parts[1:])
    try:
        return float(s)
    except ValueError:
        return None

df['lat_clean'] = df['Vĩ độ'].apply(clean_coord)
df['lon_clean'] = df['Kinh độ'].apply(clean_coord)

print("\nOutliers where lat > 30 or lat < 8:")
outliers_lat = df[(df['lat_clean'] > 30) | (df['lat_clean'] < 8)]
print(f"Count: {len(outliers_lat)}")
if len(outliers_lat) > 0:
    print(outliers_lat[['Mã SAP', 'Tên cửa hàng', 'Vĩ độ', 'Kinh độ', 'lat_clean', 'lon_clean']])

print("\nOutliers where lon > 110 or lon < 100:")
outliers_lon = df[(df['lon_clean'] > 110) | (df['lon_clean'] < 100)]
print(f"Count: {len(outliers_lon)}")
if len(outliers_lon) > 0:
    print(outliers_lon[['Mã SAP', 'Tên cửa hàng', 'Vĩ độ', 'Kinh độ', 'lat_clean', 'lon_clean']].head(10))

print("\nSuccessfully cleaned: ", df[['lat_clean', 'lon_clean']].notna().all(axis=1).sum(), "/", len(df))
