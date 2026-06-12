import os

search_dir = r"d:\Dự án AI"
for root, dirs, files in os.walk(search_dir):
    for file in files:
        full_path = os.path.join(root, file)
        if any(keyword in file.lower() for keyword in ["danh sach", "hop dong", "phu luc", "mo moi", "phan tich"]):
            print(full_path)
