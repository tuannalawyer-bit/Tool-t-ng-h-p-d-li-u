import pandas as pd
import numpy as np
import json
import sys
import io
import re
from sklearn.neighbors import BallTree
import os
import folium
from folium.plugins import MarkerCluster

# Ensure output encoding is UTF-8 for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configuration
EARTH_RADIUS = 6371000.0  # in meters
SEARCH_RADIUS = 100.0     # in meters
SEARCH_RADIUS_RAD = SEARCH_RADIUS / EARTH_RADIUS

BASE_DIR = r"d:\Dự án AI\map Ch"
STORES_FILE = os.path.join(BASE_DIR, "danh sach CH.xlsx")
AMENITIES_FILE = os.path.join(BASE_DIR, "vietnam_amenities.json")
OUTPUT_SUMMARY = os.path.join(BASE_DIR, "Tong_hop_CH.xlsx")
OUTPUT_DETAILS = os.path.join(BASE_DIR, "Chi_tiet_lan_can.xlsx")
OUTPUT_MAP = os.path.join(BASE_DIR, "ban_do_tuong_tac.html")

def clean_coordinate(val):
    if pd.isna(val):
        return None
    s = str(val).strip().replace(',', '.')
    if not s:
        return None
    
    # Remove any non-numeric chars (keep -, . and digits)
    s = re.sub(r'[^\d\.\-]', '', s)
    if not s:
        return None
        
    # If multiple dots exist, correct it to the first dot only
    if s.count('.') > 1:
        parts = s.split('.')
        s = parts[0] + '.' + "".join(parts[1:])
        
    try:
        num = float(s)
        # Corner case for large coordinates stored without decimals (e.g., 107615096)
        if abs(num) > 1000:
            num = num / 1000000.0
        # Basic lat/lon limits check
        if abs(num) > 180:
            return None
        return num
    except ValueError:
        return None

def get_amenity_category(amenity_type):
    education = ['school', 'kindergarten', 'university', 'college']
    health = ['hospital', 'clinic', 'doctors']
    if amenity_type in education:
        return 'Giáo dục'
    elif amenity_type in health:
        return 'Y tế'
    return 'Khác'

def get_amenity_vi_name(amenity_type):
    mapping = {
        'school': 'Trường học',
        'kindergarten': 'Trường mầm non',
        'university': 'Đại học',
        'college': 'Cao đẳng',
        'hospital': 'Bệnh viện',
        'clinic': 'Phòng khám',
        'doctors': 'Bác sĩ/Phòng mạch'
    }
    return mapping.get(amenity_type, amenity_type)

def main():
    print("1. Đang tải dữ liệu cửa hàng...")
    if not os.path.exists(STORES_FILE):
        print(f"Không tìm thấy file cửa hàng tại: {STORES_FILE}")
        return
    df_stores = pd.read_excel(STORES_FILE)
    print(f"Đã đọc {len(df_stores)} cửa hàng.")
    
    # Clean coordinates
    df_stores['lat_clean'] = df_stores['Vĩ độ'].apply(clean_coordinate)
    df_stores['lon_clean'] = df_stores['Kinh độ'].apply(clean_coordinate)
    
    # Separate valid coordinates
    valid_stores = df_stores[df_stores['lat_clean'].notna() & df_stores['lon_clean'].notna()].copy()
    invalid_count = len(df_stores) - len(valid_stores)
    print(f"Tọa độ hợp lệ: {len(valid_stores)} cửa hàng. (Không hợp lệ: {invalid_count})")
    
    if len(valid_stores) == 0:
        print("Không có dữ liệu tọa độ hợp lệ nào để phân tích!")
        return

    print("\n2. Đang tải dữ liệu cơ sở giáo dục/y tế OSM...")
    if not os.path.exists(AMENITIES_FILE):
        print(f"Không tìm thấy file dữ liệu OSM tại: {AMENITIES_FILE}. Vui lòng chạy fetch_amenities.py trước.")
        return
        
    with open(AMENITIES_FILE, 'r', encoding='utf-8') as f:
        osm_data = json.load(f)
        
    elements = osm_data.get('elements', [])
    print(f"Đã đọc {len(elements)} tiện ích từ OSM.")
    
    # Parse amenities
    amenities_list = []
    for el in elements:
        lat = el.get('lat')
        lon = el.get('lon')
        
        # For way/relation, Overpass 'out center' puts centroid in 'center' object
        if lat is None or lon is None:
            center = el.get('center')
            if center:
                lat = center.get('lat')
                lon = center.get('lon')
                
        if lat is None or lon is None:
            continue
            
        tags = el.get('tags', {})
        amenity_type = tags.get('amenity')
        name = tags.get('name', 'Không tên')
        
        amenities_list.append({
            'osm_id': el.get('id'),
            'name': name,
            'amenity_type': amenity_type,
            'category': get_amenity_category(amenity_type),
            'lat': lat,
            'lon': lon
        })
        
    df_amenities = pd.DataFrame(amenities_list)
    print(f"Đã lọc {len(df_amenities)} cơ sở có tọa độ hợp lệ.")
    
    print("\n3. Tiến hành phân tích bán kính 100m bằng BallTree...")
    
    # Convert coordinates to radians
    store_coords_rad = np.radians(valid_stores[['lat_clean', 'lon_clean']].values)
    amenity_coords_rad = np.radians(df_amenities[['lat', 'lon']].values)
    
    # Build Ball Tree
    tree = BallTree(amenity_coords_rad, metric='haversine')
    
    # Query radius
    indices, distances = tree.query_radius(store_coords_rad, r=SEARCH_RADIUS_RAD, return_distance=True)
    
    # Collect results
    detailed_results = []
    
    # Create summary column placeholders in valid_stores
    valid_stores['Số cơ sở giáo dục'] = 0
    valid_stores['Số cơ sở y tế'] = 0
    valid_stores['Tổng cơ sở (100m)'] = 0
    
    for i, (idx_list, dist_list) in enumerate(zip(indices, distances)):
        store_idx = valid_stores.index[i]
        store_row = valid_stores.loc[store_idx]
        
        store_sap = store_row['Mã SAP']
        store_name = store_row['Tên cửa hàng']
        
        edu_count = 0
        health_count = 0
        
        for amenity_idx, dist_rad in zip(idx_list, dist_list):
            amenity_row = df_amenities.iloc[amenity_idx]
            dist_meters = dist_rad * EARTH_RADIUS
            
            category = amenity_row['category']
            if category == 'Giáo dục':
                edu_count += 1
            elif category == 'Y tế':
                health_count += 1
                
            detailed_results.append({
                'Mã SAP cửa hàng': store_sap,
                'Tên cửa hàng': store_name,
                'Tên cơ sở lân cận': amenity_row['name'],
                'Loại cơ sở': get_amenity_vi_name(amenity_row['amenity_type']),
                'Phân nhóm': category,
                'Khoảng cách (mét)': round(dist_meters, 1),
                'Vĩ độ cơ sở': amenity_row['lat'],
                'Kinh độ cơ sở': amenity_row['lon']
            })
            
        valid_stores.at[store_idx, 'Số cơ sở giáo dục'] = edu_count
        valid_stores.at[store_idx, 'Số cơ sở y tế'] = health_count
        valid_stores.at[store_idx, 'Tổng cơ sở (100m)'] = edu_count + health_count
        
    print(f"Phân tích xong. Đã tìm thấy tổng cộng {len(detailed_results)} mối liên hệ lân cận.")
    
    print("\n4. Đang xuất các báo cáo Excel...")
    # Update main df with results
    df_final_summary = df_stores.copy()
    df_final_summary['Số cơ sở giáo dục'] = 0
    df_final_summary['Số cơ sở y tế'] = 0
    df_final_summary['Tổng cơ sở (100m)'] = 0
    
    # Re-integrate valid stores statistics back to full dataframe
    for col in ['Số cơ sở giáo dục', 'Số cơ sở y tế', 'Tổng cơ sở (100m)']:
        df_final_summary.loc[valid_stores.index, col] = valid_stores[col]
        
    # Output summaries
    df_final_summary.to_excel(OUTPUT_SUMMARY, index=False)
    print(f"Đã lưu tóm tắt cửa hàng tại: {OUTPUT_SUMMARY}")
    
    df_details = pd.DataFrame(detailed_results)
    if len(df_details) > 0:
        df_details.to_excel(OUTPUT_DETAILS, index=False)
        print(f"Đã lưu chi tiết tiện ích lân cận tại: {OUTPUT_DETAILS}")
    else:
        print("Không tìm thấy tiện ích nào trong bán kính 100m, không tạo file chi tiết.")
        
    print("\n5. Tạo bản đồ tương tác HTML...")
    # Center the map around the median coordinate of valid stores
    center_lat = valid_stores['lat_clean'].median()
    center_lon = valid_stores['lon_clean'].median()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="OpenStreetMap")
    
    # Clusters
    marker_cluster_stores = MarkerCluster(name="Cửa hàng (Đã nhóm)").add_to(m)
    
    # Feature Groups for filtering
    fg_edu = folium.FeatureGroup(name="Cơ sở giáo dục lân cận (<100m)", show=True).add_to(m)
    fg_health = folium.FeatureGroup(name="Cơ sở y tế lân cận (<100m)", show=True).add_to(m)
    
    # Keep track of which amenities have been added to avoid duplicates on map
    added_amenity_ids = set()
    
    # We add stores to cluster
    for _, row in valid_stores.iterrows():
        lat, lon = row['lat_clean'], row['lon_clean']
        sap = row['Mã SAP']
        name = row['Tên cửa hàng']
        n_edu = row['Số cơ sở giáo dục']
        n_health = row['Số cơ sở y tế']
        
        popup_text = f"""
        <div style="font-family: sans-serif; width: 220px;">
            <h4 style="margin: 0 0 5px 0; color: #1a73e8;">{name}</h4>
            <b>Mã SAP:</b> {sap}<br>
            <hr style="margin: 5px 0;">
            <span style="color: blue;">📚 Giáo dục lân cận: {n_edu}</span><br>
            <span style="color: red;">🏥 Y tế lân cận: {n_health}</span>
        </div>
        """
        
        # Color marker based on whether it has amenities
        marker_color = 'green' if (n_edu + n_health) > 0 else 'gray'
        
        # Add store marker
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color=marker_color, icon='shopping-cart', prefix='fa'),
            tooltip=name
        ).add_to(marker_cluster_stores)
        
        # Add 100m circle ONLY if there's at least one facility nearby to keep map clean
        if (n_edu + n_health) > 0:
            folium.Circle(
                location=[lat, lon],
                radius=SEARCH_RADIUS,
                color='orange',
                fill=True,
                fill_color='orange',
                fill_opacity=0.15,
                weight=1,
                tooltip="Phạm vi 100m"
            ).add_to(m)
            
    # Add found amenities to the map
    # Re-traverse indices or use the detailed_results to plot matched amenities
    plotted_amenities_count = 0
    for index, row in df_details.iterrows():
        # Use combination of lat, lon, name as unique key if we want
        amenity_key = f"{row['Vĩ độ cơ sở']}_{row['Kinh độ cơ sở']}_{row['Tên cơ sở lân cận']}"
        
        if amenity_key in added_amenity_ids:
            continue
            
        added_amenity_ids.add(amenity_key)
        lat, lon = row['Vĩ độ cơ sở'], row['Kinh độ cơ sở']
        name = row['Tên cơ sở lân cận']
        cat = row['Phân nhóm']
        vi_type = row['Loại cơ sở']
        
        popup_text = f"""
        <div style="font-family: sans-serif; width: 200px;">
            <h4 style="margin: 0 0 5px 0;">{name}</h4>
            <b>Phân loại:</b> {vi_type}<br>
            <b>Nhóm:</b> {cat}
        </div>
        """
        
        if cat == 'Giáo dục':
            icon = folium.Icon(color='blue', icon='book', prefix='fa')
            target_fg = fg_edu
        else:
            icon = folium.Icon(color='red', icon='plus-square', prefix='fa')
            target_fg = fg_health
            
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=250),
            icon=icon,
            tooltip=f"{vi_type}: {name}"
        ).add_to(target_fg)
        plotted_amenities_count += 1
        
    folium.LayerControl().add_to(m)
    m.save(OUTPUT_MAP)
    print(f"Đã lưu bản đồ tương tác HTML tại: {OUTPUT_MAP}")
    print(f"Đã vẽ {plotted_amenities_count} cơ sở lân cận độc lập lên bản đồ.")
    print("\n=== HOÀN THÀNH ===")

if __name__ == "__main__":
    main()
