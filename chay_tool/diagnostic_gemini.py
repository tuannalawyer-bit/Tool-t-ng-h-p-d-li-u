import sys
import os
import json

try:
    api_key_path = "d:\\Dự án AI\\chay_tool\\gemini_api_key.txt"
    if not os.path.exists(api_key_path):
        api_key_path = "D:\\chạy tool\\chạy tool\\gemini_api_key.txt"
        
    with open(api_key_path, "r") as f:
        key = f.read().strip()
    
    print(f"[*] Loaded API key starting with: {key[:10]}...")
    
    from google import genai
    client = genai.Client(api_key=key)
    
    print("\n[*] Testing 'gemini-2.5-flash' with a tiny prompt...")
    try:
        r1 = client.models.generate_content(model='gemini-2.5-flash', contents="Hi, respond 'OK'")
        print(f"[SUCCESS 2.5 FLASH]: {r1.text.strip()}")
    except Exception as e:
        print(f"[FAILED 2.5 FLASH]: {e}")

    print("\n[*] Testing 'gemini-1.5-flash' (The ultimate baseline fallback)...")
    try:
        r2 = client.models.generate_content(model='gemini-1.5-flash', contents="Hi, respond 'OK'")
        print(f"[SUCCESS 1.5 FLASH]: {r2.text.strip()}")
    except Exception as e:
        print(f"[FAILED 1.5 FLASH]: {e}")
        
    print("\n[*] Testing 'gemini-2.0-flash-exp'...")
    try:
        r3 = client.models.generate_content(model='gemini-2.0-flash-exp', contents="Hi, respond 'OK'")
        print(f"[SUCCESS 2.0 EXP]: {r3.text.strip()}")
    except Exception as e:
        print(f"[FAILED 2.0 EXP]: {e}")

except Exception as e:
    print(f"\n[GLOBAL CRITICAL]: {e}")
