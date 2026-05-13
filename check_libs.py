import sys
import io

# Fix printing encoding issues on Windows console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("Starting library load verification...")

try:
    import google.generativeai as genai
    print("SUCCESS: google-generativeai loaded")
except Exception as e:
    print("ERROR loading google-generativeai:", e)

try:
    import easyocr
    print("SUCCESS: easyocr loaded")
except Exception as e:
    print("ERROR loading easyocr:", e)

print("Verification finished.")
