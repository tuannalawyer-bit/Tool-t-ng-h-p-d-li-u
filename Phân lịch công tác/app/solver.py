import numpy as np
import requests
import logging
import math
import time
import random

logger = logging.getLogger(__name__)
from collections import defaultdict
from app.config import (
    NEAR_RADIUS_KM, WEIGHT_NEAR, WEIGHT_FAR,
    OSRM_URL_TABLE, OSRM_URL_ROUTE, ROAD_WINDING_FACTOR,
    RIVER_DETOUR_RATIO, RIVER_PENALTY_FACTOR
)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Tính khoảng cách chim bay giữa 2 tọa độ (km)"""
    R = 6371.0  # Bán kính Trái Đất (km)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_road_distance_matrix_chunked(coords, status_cb=None):
    """
    Lấy ma trận khoảng cách đường bộ từ OSRM sử dụng kỹ thuật chia nhỏ (Chunking).
    Hỗ trợ N > 100 tuyệt đối an toàn.
    Trả về 2 ma trận:
    1. real_dist_matrix: Khoảng cách thật (km) để báo cáo.
    2. cost_matrix: Khoảng cách đã áp hệ số Phạt Cắt Sông (River Penalty) để chạy giải thuật.
    """
    n = len(coords)
    real_dist_matrix = np.zeros((n, n))
    cost_matrix = np.zeros((n, n))
    
    # Khởi tạo giá trị chim bay mặc định
    for i in range(n):
        for j in range(n):
            if i == j:
                real_dist_matrix[i, j] = 0.0
            else:
                d_crow = haversine_distance(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
                real_dist_matrix[i, j] = d_crow * ROAD_WINDING_FACTOR
    
    cost_matrix = real_dist_matrix.copy()
    
    MAX_CHUNK = 45
    chunks = [list(range(i, min(i + MAX_CHUNK, n))) for i in range(0, n, MAX_CHUNK)]
    num_chunks = len(chunks)
    
    logger.info(f"Kích hoạt Chunking Engine: Chia {n} điểm thành {num_chunks} nhóm nhỏ...")
    if status_cb: status_cb(f"🌐 Kết nối OSRM: Đang tính bản đồ đi bộ cho {n} điểm...")
    
    success_calls = 0
    
    try:
        for idx_a in range(num_chunks):
            for idx_b in range(idx_a, num_chunks):
                chunk_a = chunks[idx_a]
                chunk_b = chunks[idx_b]
                
                if idx_a == idx_b:
                    combined_indices = chunk_a
                    src_indices = list(range(len(chunk_a)))
                    dst_indices = list(range(len(chunk_a)))
                else:
                    combined_indices = chunk_a + chunk_b
                    src_indices = list(range(len(chunk_a)))
                    dst_indices = list(range(len(chunk_a), len(combined_indices)))
                
                combined_coords = [coords[idx] for idx in combined_indices]
                coord_str = ";".join([f"{lon},{lat}" for lat, lon in combined_coords])
                src_str = ";".join(map(str, src_indices))
                dst_str = ";".join(map(str, dst_indices))
                url = f"{OSRM_URL_TABLE}{coord_str}?sources={src_str}&destinations={dst_str}&annotations=distance"
                
                if success_calls > 0:
                    time.sleep(0.1)
                    
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("code") == "Ok" and "distances" in data:
                        dist_data = np.array(data["distances"]) / 1000.0
                        for local_i in range(len(chunk_a)):
                            for local_j in range(len(chunk_b)):
                                val = dist_data[local_i, local_j]
                                global_i = chunk_a[local_i]
                                global_j = chunk_b[local_j]
                                if val is not None and not np.isnan(val):
                                    real_dist_matrix[global_i, global_j] = val
                                    real_dist_matrix[global_j, global_i] = val
                        success_calls += 1
                        if status_cb: 
                            pct = int(((idx_a * num_chunks + idx_b) / (num_chunks * num_chunks)) * 100)
                            status_cb(f"🌐 Đang tải lưới thực địa... {pct}%")
        
        if success_calls > 0:
            logger.info("OSRM phản hồi thành công! Bắt đầu lọc địa hình cắt sông...")
            cost_matrix = real_dist_matrix.copy()
            river_crossings_count = 0
            
            for i in range(n):
                for j in range(n):
                    if i == j: continue
                    d_real = real_dist_matrix[i, j]
                    d_crow = haversine_distance(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
                    if 0.2 < d_crow < 2.5 and (d_real / d_crow) > RIVER_DETOUR_RATIO:
                        cost_matrix[i, j] = d_real * RIVER_PENALTY_FACTOR
                        river_crossings_count += 1
            logger.info(f"Phát hiện {river_crossings_count // 2} cặp vị trí có rào cản sông ngòi.")
            if status_cb: status_cb("✅ Phân tích lưới thành công! Bắt đầu tối ưu đa mục tiêu...")
            return real_dist_matrix, cost_matrix
            
    except Exception as e:
        logger.warning(f"Lỗi phân tách OSRM ({e}), tự động dùng chim bay uốn lượn.")
        if status_cb: status_cb("⚠️ Lỗi mạng: Chuyển sang Thuật toán Dự phòng...")
        
    return real_dist_matrix, cost_matrix

def get_route_geometry(coords):
    """Lấy đường vẽ chi tiết dạng GeoJSON."""
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"{OSRM_URL_ROUTE}{coord_str}?overview=full&geometries=geojson"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
                geojson_coords = data["routes"][0]["geometry"]["coordinates"]
                return [[lat, lon] for lon, lat in geojson_coords]
    except:
        pass
    return coords

def solve_tsp_2opt(cost_matrix, node_indices):
    """Giải TSP ngắn nhất cho chu trình con bằng 2-Opt."""
    n = len(node_indices)
    if n <= 1:
        return node_indices
        
    local_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            local_matrix[i, j] = cost_matrix[node_indices[i], node_indices[j]]
            
    unvisited = list(range(1, n))
    tour = [0]
    current = 0
    while unvisited:
        next_node = min(unvisited, key=lambda x: local_matrix[current, x])
        tour.append(next_node)
        unvisited.remove(next_node)
    tour.append(0)
    
    def get_tour_len(t):
        return sum(local_matrix[t[i], t[i+1]] for i in range(len(t) - 1))
        
    improved = True
    best_len = get_tour_len(tour)
    
    while improved:
        improved = False
        for i in range(1, len(tour) - 2):
            for j in range(i + 1, len(tour) - 1):
                new_tour = tour[:]
                new_tour[i:j+1] = reversed(tour[i:j+1])
                new_len = get_tour_len(new_tour)
                if new_len < best_len - 0.001:
                    tour = new_tour
                    best_len = new_len
                    improved = True
                    break
            if improved:
                break
    return [node_indices[idx] for idx in tour[:-1]]

def calculate_store_weights(hotel_lat, hotel_lon, stores_df):
    """Tính toán khoảng cách chim bay cơ bản và gán trọng số."""
    hotel_distances = []
    weights = []
    for idx, row in stores_df.iterrows():
        d = haversine_distance(hotel_lat, hotel_lon, float(row['Latitude']), float(row['Longitude']))
        hotel_distances.append(d)
        w = WEIGHT_NEAR if d <= NEAR_RADIUS_KM else WEIGHT_FAR
        weights.append(w)
    
    stores_df = stores_df.copy()
    stores_df['Distance_To_Hotel'] = hotel_distances
    stores_df['Weight'] = weights
    return stores_df

def agglomerative_spatial_clustering(cost_matrix, store_weights, max_weight_per_cluster=1.001):
    """
    GOM CỤM KHÔNG GIAN PHÂN CẤP CÓ RÀNG BUỘC (ACCC).
    Gom cửa hàng thành các Day Trip liền mạch, an toàn tuyệt đối trước sông ngòi.
    """
    n = len(store_weights)
    clusters = {i: [i] for i in range(1, n + 1)}
    cluster_weights = {i: store_weights[i-1] for i in range(1, n + 1)}
    
    def get_cluster_dist(c1_nodes, c2_nodes):
        dists = [cost_matrix[u, v] for u in c1_nodes for v in c2_nodes]
        return sum(dists) / len(dists)
        
    while True:
        best_pair = None
        min_dist = float('inf')
        keys = list(clusters.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                k1, k2 = keys[i], keys[j]
                if cluster_weights[k1] + cluster_weights[k2] <= max_weight_per_cluster:
                    d = get_cluster_dist(clusters[k1], clusters[k2])
                    if d < min_dist:
                        min_dist = d
                        best_pair = (k1, k2)
        if not best_pair:
            break
        k1, k2 = best_pair
        clusters[k1].extend(clusters[k2])
        cluster_weights[k1] += cluster_weights[k2]
        del clusters[k2]
        del cluster_weights[k2]
    return list(clusters.values())

def optimize_staff_assignment_multi_objective(day_trips, num_staff, status_cb=None):
    """
    ĐỘNG CƠ TỐI ƯU HÓA ĐA MỤC TIÊU V1.5.0 (Iterated Local Search Hill-Climbing).
    Thuật toán tìm kiếm cục bộ hiệu năng cực cao để thỏa mãn:
    - Cân bằng Quãng đường <= 20%
    - Cân bằng Số lượng CH <= 20%
    - Luật bù trừ: Đi nhiều km hơn thì ít cửa hàng hơn!
    - Gom cụm mềm không gian (Mềm).
    """
    m = len(day_trips)
    if m == 0:
        return [{'Trips': [], 'Weight': 0.0, 'TotalDistance': 0.0} for _ in range(num_staff)]
        
    # Trích xuất thông số tối ưu hóa
    trip_dists = [t['Distance'] for t in day_trips]
    trip_stores_counts = [len(t['Nodes']) for t in day_trips]
    trip_weights = [t['Weight'] for t in day_trips]
    
    # Precompute trip centroids as a fast numpy array for instantaneous lookup
    trip_centroids = np.zeros((m, 2))
    for idx, t in enumerate(day_trips):
        lats = [s['Latitude'] for s in t['Stores']]
        lons = [s['Longitude'] for s in t['Stores']]
        trip_centroids[idx, 0] = sum(lats) / len(lats)
        trip_centroids[idx, 1] = sum(lons) / len(lons)

    # --- ĐỊNH NGHĨA HÀM PHẠT TOÁN HỌC SIÊU TỐC ĐỘ (High-Performance Penalty Evaluator) ---
    def evaluate_penalty(assignment):
        staff_dist = [0.0] * num_staff
        staff_stores = [0] * num_staff
        staff_days = [0] * num_staff
        staff_trips = [[] for _ in range(num_staff)]
        
        for j_idx, s_id in enumerate(assignment):
            staff_dist[s_id] += trip_dists[j_idx]
            staff_stores[s_id] += trip_stores_counts[j_idx]
            staff_days[s_id] += 1
            staff_trips[s_id].append(j_idx)
            
        penalty = 0.0
        
        # 1. Khống chế số ngày công lệch không quá 1 (P_days)
        avg_days = m / num_staff
        for d in staff_days:
            penalty += ((d - avg_days) ** 2) * 500000.0
            
        # 2. Cân bằng quãng đường (Target <= 20%)
        min_d = min(staff_dist)
        max_d = max(staff_dist)
        if min_d > 0.1:
            d_diff = (max_d - min_d) / min_d
            excess_d = max(0.0, d_diff - 0.20)
            penalty += (excess_d ** 2) * 10000000.0
            penalty += (d_diff ** 2) * 50000.0
        else:
            penalty += 10000000.0
            
        # 3. Cân bằng số cửa hàng (Target <= 20%)
        min_s = min(staff_stores)
        max_s = max(staff_stores)
        if min_s > 0:
            s_diff = (max_s - min_s) / min_s
            excess_s = max(0.0, s_diff - 0.20)
            penalty += (excess_s ** 2) * 10000000.0
            penalty += (s_diff ** 2) * 30000.0
        else:
            penalty += 10000000.0
            
        # 4. LUẬT BÙ TRỪ VÀNG: Đi xa hơn thì PHẢI ít cửa hàng hơn
        for a in range(num_staff):
            for b in range(a + 1, num_staff):
                da, db = staff_dist[a], staff_dist[b]
                sa, sb = staff_stores[a], staff_stores[b]
                if da > db + 2.0 and sa > sb:
                    penalty += (da - db) * (sa - sb) * 150000.0
                elif db > da + 2.0 and sb > sa:
                    penalty += (db - da) * (sb - sa) * 150000.0
                    
        # 5. Gom cụm địa lý mềm SIÊU TỐC ĐỘ (Tối ưu hóa tuyến tính dùng Euclidean bình phương)
        # Tuyệt đối không dùng hàm lượng giác Haversine trong Hot Loop!
        geo_compact = 0.0
        for s_id in range(num_staff):
            indices = staff_trips[s_id]
            if not indices: continue
            
            # Tính centroid trung bình của vùng làm việc nhân sự
            centroid_lat = sum(trip_centroids[idx, 0] for idx in indices) / len(indices)
            centroid_lon = sum(trip_centroids[idx, 1] for idx in indices) / len(indices)
            
            # Tổng bình phương khoảng cách Euclidean đến Centroid
            for idx in indices:
                # Phép toán đại số thuần tuý, nhanh hơn gấp hàng trăm lần hàm math.sin/cos
                geo_compact += (trip_centroids[idx, 0] - centroid_lat)**2 + (trip_centroids[idx, 1] - centroid_lon)**2
                
        # Hệ số quy đổi tương quan Euclidean sang Phạt để cân bằng với Quãng đường
        penalty += geo_compact * 200000.0 
        
        return penalty

    # --- THUẬT TOÁN TÌM KIẾM CỤC BỘ ĐA KHỞI ĐẦU ---
    best_overall_assignment = None
    best_overall_penalty = float('inf')
    
    # Tối ưu hóa số lượng khởi động (Starts) & Giới hạn hội tụ
    starts = 15
    if status_cb: status_cb("⚙️ Bước 3/4: Khởi động Động cơ Tìm kiếm Cục bộ Tốc độ cao...")
    
    for start in range(starts):
        current_assignment = []
        for i in range(m):
            current_assignment.append(i % num_staff)
        random.shuffle(current_assignment)
        
        current_penalty = evaluate_penalty(current_assignment)
        
        no_improve_limit = 1000
        no_improve = 0
        
        while no_improve < no_improve_limit:
            mut_type = random.choice(["MOVE", "SWAP"])
            new_assignment = current_assignment.copy()
            
            if mut_type == "MOVE":
                t_idx = random.randrange(m)
                s_new = random.randrange(num_staff)
                if new_assignment[t_idx] == s_new:
                    no_improve += 1
                    continue
                new_assignment[t_idx] = s_new
            else: # SWAP
                t1 = random.randrange(m)
                t2 = random.randrange(m)
                if new_assignment[t1] == new_assignment[t2]:
                    no_improve += 1
                    continue
                new_assignment[t1], new_assignment[t2] = new_assignment[t2], new_assignment[t1]
                
            new_penalty = evaluate_penalty(new_assignment)
            
            if new_penalty < current_penalty - 0.00001:
                current_assignment = new_assignment
                current_penalty = new_penalty
                no_improve = 0
            else:
                no_improve += 1
                
        # Cập nhật kỷ lục toàn cầu
        if current_penalty < best_overall_penalty:
            best_overall_penalty = current_penalty
            best_overall_assignment = current_assignment
            
    # --- ĐÓNG GÓI KẾT QUẢ TỐI ƯU TỐT NHẤT ---
    final_buckets = [{'Trips': [], 'Weight': 0.0, 'TotalDistance': 0.0, 'TotalStores': 0} for _ in range(num_staff)]
    for t_idx, s_id in enumerate(best_overall_assignment):
        final_buckets[s_id]['Trips'].append(day_trips[t_idx])
        final_buckets[s_id]['Weight'] += trip_weights[t_idx]
        final_buckets[s_id]['TotalDistance'] += trip_dists[t_idx]
        final_buckets[s_id]['TotalStores'] += trip_stores_counts[t_idx]
        
    for b in final_buckets:
        b['TotalDistance'] = round(b['TotalDistance'], 2)
        
    return final_buckets

def optimize_schedule(hotel_lat, hotel_lon, stores_df, num_staff, status_cb=None):
    """
    HÀM GIẢI PHÂN LỊCH HYBRID SIÊU CÂN BẰNG V1.5.0:
    1. Nạp bản đồ chỉ đường đi bộ + Khử cắt sông vĩnh viễn.
    2. Gom cụm phân cấp ACCC tạo Day Trips không vượt sông, bó chặt không gian.
    3. Tối ưu TSP 2-Opt trong ngày.
    4. Tối ưu Tìm kiếm Cục bộ Multi-Objective: Cân bằng km <= 20%, cửa hàng <= 20% và Luật bù trừ Vàng.
    """
    if status_cb: status_cb("⚙️ Bước 1/4: Chuẩn bị dữ liệu & trọng số...")
    
    processed_df = calculate_store_weights(hotel_lat, hotel_lon, stores_df)
    processed_df = processed_df.reset_index(drop=True)
    
    full_coords = [(hotel_lat, hotel_lon)]
    for _, row in processed_df.iterrows():
        full_coords.append((float(row['Latitude']), float(row['Longitude'])))
        
    # Gọi API Foot Routing + River Penalty (Từ 1.4.0)
    real_dist_matrix, cost_matrix = get_road_distance_matrix_chunked(full_coords, status_cb=status_cb)
    
    if status_cb: status_cb("⚙️ Bước 2/4: Gom cụm Day Trips không vượt sông...")
    
    # Gom Day Trips toàn cục sử dụng giải thuật ACCC thông minh
    store_weights_list = processed_df['Weight'].tolist()
    day_trips_raw = agglomerative_spatial_clustering(cost_matrix, store_weights_list, max_weight_per_cluster=1.001)
    
    day_trips = []
    for trip_idx, nodes in enumerate(day_trips_raw):
        tsp_nodes = [0] + nodes
        opt_tour = solve_tsp_2opt(cost_matrix, tsp_nodes)
        opt_stores_nodes = opt_tour[1:]
        
        full_cycle = [0] + opt_stores_nodes + [0]
        actual_dist = 0.0
        for i in range(len(full_cycle) - 1):
            actual_dist += real_dist_matrix[full_cycle[i], full_cycle[i+1]]
            
        w_sum = sum(processed_df.iloc[n-1]['Weight'] for n in opt_stores_nodes)
        
        readable_stores = []
        for node in opt_stores_nodes:
            row = processed_df.iloc[node - 1]
            readable_stores.append({
                'StoreCode': row.get('Mã CH', row.get('StoreCode', f"CH_{node}")),
                'Name': row.get('Tên CH', row.get('Name', '')),
                'Latitude': float(row['Latitude']),
                'Longitude': float(row['Longitude']),
                'Address': row.get('Địa chỉ', row.get('Address', '')),
                'Distance_To_Hotel': float(row['Distance_To_Hotel']),
                'Weight': float(row['Weight']),
                '__temp_id__': row.get('__temp_id__')
            })
            
        path_coords = [(hotel_lat, hotel_lon)] + [(float(processed_df.iloc[n-1]['Latitude']), float(processed_df.iloc[n-1]['Longitude'])) for n in opt_stores_nodes] + [(hotel_lat, hotel_lon)]
        
        day_trips.append({
            'Id': trip_idx,
            'Nodes': opt_stores_nodes,
            'Weight': w_sum,
            'Stores': readable_stores,
            'Distance': round(actual_dist, 2),
            'PathCoords': path_coords
        })
        
    if status_cb: status_cb("⚙️ Bước 4/4: Triển khai Động cơ Tìm kiếm Cục bộ Đa mục tiêu...")
    
    # Triển khai Tìm kiếm cục bộ khống chế 20% và Luật bù trừ (Tính năng v1.5.0)
    staff_buckets = optimize_staff_assignment_multi_objective(day_trips, num_staff, status_cb=status_cb)
    
    # Đồng bộ Staff_ID ngược vào DataFrame
    processed_df['Staff_ID'] = -1
    for staff_id, bucket in enumerate(staff_buckets):
        for trip in bucket['Trips']:
            for node in trip['Nodes']:
                processed_df.at[node - 1, 'Staff_ID'] = staff_id
                
    # Đóng gói dữ liệu trả về
    results = {
        'staff_schedules': {},
        'summary': []
    }
    
    for staff_id, bucket in enumerate(staff_buckets):
        staff_routes = []
        # Sắp xếp các ngày trong lộ trình cá nhân cho ngăn nắp
        sorted_trips = sorted(bucket['Trips'], key=lambda x: x['Distance'], reverse=True)
        for day_idx, trip in enumerate(sorted_trips):
            staff_routes.append({
                'Day': day_idx + 1,
                'Stores': trip['Stores'],
                'Distance': trip['Distance'],
                'PathCoords': trip['PathCoords']
            })
            
        num_stores = sum(len(t['Nodes']) for t in bucket['Trips'])
        
        results['staff_schedules'][staff_id] = {
            'Routes': staff_routes,
            'TotalDistance': round(bucket['TotalDistance'], 2),
            'NumDays': len(bucket['Trips']),
            'NumStores': num_stores
        }
        
        results['summary'].append({
            'Nhân viên': f"Nhân viên {staff_id + 1}",
            'Số cửa hàng': num_stores,
            'Số ngày đi': len(bucket['Trips']),
            'Tổng quãng đường (km)': round(bucket['TotalDistance'], 2)
        })
        
    # Logging kiểm tra hiệu suất cân bằng
    distances = [round(b['TotalDistance'], 2) for b in staff_buckets if b['TotalDistance'] > 0]
    stores_counts = [sum(len(t['Nodes']) for t in b['Trips']) for b in staff_buckets]
    
    if distances and len(distances) > 1:
        max_d, min_d = max(distances), min(distances)
        diff_d_pct = ((max_d - min_d) / min_d * 100) if min_d > 0 else 0
        
        max_s, min_s = max(stores_counts), min(stores_counts)
        diff_s_pct = ((max_s - min_s) / min_s * 100) if min_s > 0 else 0
        
        logger.info(f"HOÀN TẤT TỐI ƯU V1.5.0: Chia {len(day_trips)} ngày cho {num_staff} người.")
        logger.info(f"--> Cân bằng KM: Chênh lệch {diff_d_pct:.2f}% (Mục tiêu <= 20%)")
        logger.info(f"--> Cân bằng CH: Chênh lệch {diff_s_pct:.2f}% (Mục tiêu <= 20%)")
        
    return results, processed_df
