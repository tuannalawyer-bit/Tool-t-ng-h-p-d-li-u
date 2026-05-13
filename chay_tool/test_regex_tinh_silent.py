import re
import json

subjects = [
    "RE: Thẩm định thực địa MB: Số 23 đường Nghi Tân, Đông Mai, Quảng Ninh (MB07985)",
    "RE: Thẩm định thực địa MB: Số 64 đường Bắc Hồng, Thôn Quan Âm, Hà Nội (MB07792)",
    "Thẩm định MB Số 2 Lý Thái Tổ - Thái Bình (MB01234)"
]

res = []
for s in subjects:
    # This pattern captures the last piece of text delimiter-separated before the parenthesis
    m = re.search(r'(?:,\s*|_\s*|[:\-]\s*|^)([^,_\-:]+?)\s*\((?:MB|MN)\d+', s, re.IGNORECASE)
    if m:
        res.append({"s": s, "tinh": m.group(1).strip()})
        
with open(r"d:\Dự án AI\chay_tool\regex_test_out.json", 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=4, ensure_ascii=False)
