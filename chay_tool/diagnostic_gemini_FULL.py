import sys
import os
import json

try:
    api_key_path = "d:\\Dự án AI\\chay_tool\\gemini_api_key.txt"
    with open(api_key_path, "r") as f:
        key = f.read().strip()
    
    from google import genai
    client = genai.Client(api_key=key)
    
    # Simulated payload from the prompt we wrote
    prompt = """Bạn là một AI Chuyên gia phân tích dữ liệu Thẩm định mặt bằng bán lẻ. Hãy đọc kỹ Email và trả về kết quả JSON.

NỘI DUNG EMAIL:
\"\"\"
KSTT phản hồi kết quả thẩm định: Giá thuê mặt bằng này hiện tại khá tốt, chưa có bất thường. Tuy nhiên hồ sơ thiếu sổ đỏ chính chủ.
\"\"\"

NHIỆM VỤ: Suy luận logic và điền các trường sau vào JSON duy nhất:
- 'gia_thue_sum': Phân tích phần Giá thuê & Chi phí. Nếu giá ổn định/đạt/hợp lý, ghi chính xác cụm từ 'chưa có bất thường'. Nếu có bất thường, hãy TÓM TẮT CHI TIẾT lý do.
- 'hspl': Phân tích Hồ sơ pháp lý. Liệt kê GIẤY TỜ THIẾU hoặc RỦI RO THỰC TẾ. LƯU Ý: Tuyệt đối KHÔNG coi việc 'Sổ chưa ghi nhận nhà trên đất' là rủi ro pháp lý. Nếu không có rủi ro khác, ghi 'Đầy đủ, không có rủi ro'.
- 'ghi_chu': Tổng hợp rủi ro MB dưới dạng CÁC GẠCH ĐẦU DÒNG SIÊU CÔ ĐỌNG, NGẮN GỌN (dưới 10 từ mỗi ý). Bỏ qua các câu diễn giải thừa.

CHỈ TRẢ VỀ JSON CHỨA CÁC KEY: "gia_thue_sum", "hspl", "ghi_chu"
"""
    print("[*] Sending FULL payload with response_mime_type='application/json' configuration...")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        print("\n[RAW RESPONSE]:")
        print(response.text)
        
        parsed = json.loads(response.text)
        print("\n[JSON PARSE SUCCESS]:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except Exception as inner_e:
        print(f"\n[INNER FAILED]: {inner_e}")

except Exception as e:
    print(f"\n[GLOBAL FAILURE]: {e}")
