import re

subjects = [
    "RE: Thẩm định thực địa MB: Số 23 đường Nghi Tân, Đông Mai, Quảng Ninh (MB07985)",
    "RE: Thẩm định thực địa MB: Số 64 đường Bắc Hồng, Thôn Quan Âm, Hà Nội (MB07792)",
    "Thẩm định MB Số 2 Lý Thái Tổ - Thái Bình (MB01234)"
]

for s in subjects:
    # Goal: Capture the word/words just before the parenthesis (MB... or MN...)
    # We can split by comma/underscore and look at the last component before parenthesis
    m = re.search(r'(?:,\s*|_\s*|[:\-]\s*|^)([^,_\-:]+?)\s*\((?:MB|MN)\d+', s, re.IGNORECASE)
    if m:
        print(f"MATCH '{s}' -> '{m.group(1).strip()}'")
    else:
        # Alternative simpler catch-all
        parts = re.split(r'[,\-_:]', re.sub(r'\((?:MB|MN)\d+.*', '', s))
        tinh = parts[-1].strip() if parts else ""
        print(f"ALT '{s}' -> '{tinh}'")
