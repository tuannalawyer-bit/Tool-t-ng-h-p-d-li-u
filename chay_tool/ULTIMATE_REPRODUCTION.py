import sys
import os
import json

# Ensure we use the exact current module in d:\Dự án AI\chay_tool
sys.path.append(r"d:\Dự án AI\chay_tool")

try:
    import core_logic
    
    # 1. Init Gemini
    api_key_path = "d:\\Dự án AI\\chay_tool\\gemini_api_key.txt"
    with open(api_key_path, "r") as f:
        key = f.read().strip()
    core_logic.init_gemini(key)
    
    # 2. Target real file
    email_path = r"D:\chạy tool\chạy tool\emails\done_RE_   20260116_Thẩm định AN_ Mặt bằng mở mới (MB)_Đường 477C Đồng Chưa_ TT_ Thịnh Vượng_ H_ Gia Viễn_ T_ Ninh Bình.msg"
    
    print(f"[*] Calling process_msg_file on real target...")
    
    # Capture all logged callbacks to memory
    log_history = []
    def tracker(msg, tag=""):
        log_history.append(f"[{tag}] {msg}")
        
    res = core_logic.process_msg_file(email_path, log_callback=tracker)
    
    # Write state out
    with open("d:\\Dự án AI\\chay_tool\\FORENSIC_OUTPUT.json", "w", encoding="utf-8") as f:
        json.dump({
            "app_result_success": res["success"],
            "app_error": res.get("error", ""),
            "log_trail": log_history,
            "data_dump": {k: str(v) for k,v in res.get("data", {}).items()} if res.get("data") else None
        }, f, ensure_ascii=False, indent=2)

except Exception as e:
    with open("d:\\Dự án AI\\chay_tool\\FORENSIC_OUTPUT.json", "w", encoding="utf-8") as f:
        import traceback
        json.dump({
            "fatal": str(e),
            "trace": traceback.format_exc()
        }, f, ensure_ascii=False, indent=2)
