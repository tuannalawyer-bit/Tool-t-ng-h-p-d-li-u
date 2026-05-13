import sys
import os
import json

log_path = "d:\\Dự án AI\\chay_tool\\REAL_GEMINI_TEST_RESULT.json"

try:
    api_key_path = "d:\\Dự án AI\\chay_tool\\gemini_api_key.txt"
    with open(api_key_path, "r") as f:
        key = f.read().strip()
    
    from google import genai
    client = genai.Client(api_key=key)
    
    prompt = "Analyze this and return JSON: 'Giá thuê ổn'."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({
            "status": "SUCCESS",
            "raw_text": response.text
        }, f, ensure_ascii=False)

except Exception as e:
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({
            "status": "FAILED",
            "error": str(e)
        }, f, ensure_ascii=False)
