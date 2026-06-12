import folium
from folium import plugins
import os
import webbrowser
import tempfile
from app.config import COLOR_PALETTE
from app.solver import get_route_geometry

def generate_interactive_map(hotel_lat, hotel_lon, results):
    """
    Tạo bản đồ Folium cực nhanh chứa toàn bộ lộ trình của các nhân sự.
    Lưu tệp HTML tạm thời và trả về đường dẫn tuyệt đối của tệp tin.
    Sử dụng phương pháp vẽ đường thẳng tốc độ cao để đảm bảo không bao giờ bị treo đơ mạng.
    """
    # Khởi tạo bản đồ tập trung vào khách sạn
    m = folium.Map(location=[hotel_lat, hotel_lon], zoom_start=12, control_scale=True)
    
    folium.TileLayer('openstreetmap', name='Bản đồ thường').add_to(m)
    folium.TileLayer('cartodbpositron', name='Bản đồ tối giản (Load nhanh)').add_to(m)
    
    # Vẽ điểm Khách sạn/Văn phòng chính
    folium.Marker(
        location=[hotel_lat, hotel_lon],
        popup="<b>Khách sạn / Văn phòng làm việc (Điểm xuất phát)</b>",
        tooltip="Depot",
        icon=folium.Icon(color='red', icon='home', prefix='fa')
    ).add_to(m)
    
    # Duyệt vẽ cho từng nhân sự
    for staff_id, staff_data in results['staff_schedules'].items():
        staff_name = f"Nhân viên {staff_id + 1}"
        color = COLOR_PALETTE[staff_id % len(COLOR_PALETTE)]
        
        # Tạo một Group cho mỗi nhân viên
        fg = folium.FeatureGroup(name=f"{staff_name} ({staff_data['TotalDistance']} km)")
        
        for route in staff_data['Routes']:
            day = route['Day']
            path_coords = route['PathCoords']
            
            # Vẽ đường đi tốc độ cao (Straight-line PolyLine) để không phụ thuộc mạng OSRM
            folium.PolyLine(
                locations=path_coords,
                color=color,
                weight=4,
                opacity=0.75,
                dash_array='5, 10' if day % 2 == 0 else None,
                tooltip=f"{staff_name} - Ngày {day} ({route['Distance']} km)"
            ).add_to(fg)
            
            # Đặt marker cho từng cửa hàng
            for seq, store in enumerate(route['Stores']):
                store_lat = store['Latitude']
                store_lon = store['Longitude']
                
                html_popup = f"""
                <div style="font-family: Arial; width: 220px;">
                    <h4 style="margin-bottom:5px; color:{color}">{store['Name']}</h4>
                    <hr style="margin: 5px 0;">
                    <b>Mã CH:</b> {store['StoreCode']}<br>
                    <b>Địa chỉ:</b> {store['Address']}<br>
                    <b>Thứ tự:</b> {staff_name} &rarr; <b>Ngày {day}</b> (Số {seq+1})<br>
                    <b>Cách KS:</b> {store['Distance_To_Hotel']:.2f} km
                </div>
                """
                
                # Đánh số Ngày trực tiếp lên icon trên bản đồ
                folium.Marker(
                    location=[store_lat, store_lon],
                    popup=folium.Popup(html_popup, max_width=300),
                    tooltip=f"{store['Name']} (N{day}-{seq+1})",
                    icon=plugins.BeautifyIcon(
                        border_color=color,
                        text_color=color,
                        number=day,
                        inner_icon_style="margin-top:0px;",
                        background_color="white"
                    )
                ).add_to(fg)
                
        fg.add_to(m)
        
    folium.LayerControl(collapsed=False).add_to(m)
    plugins.Fullscreen(position='topright', title='Toàn màn hình', title_cancel='Thoát').add_to(m)
    plugins.MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)
    
    # Lưu tệp HTML tạm thời
    fd, path = tempfile.mkstemp(suffix='.html', prefix='Ban_Do_Lo_Trinh_')
    os.close(fd)
    
    m.save(path)
    return path

