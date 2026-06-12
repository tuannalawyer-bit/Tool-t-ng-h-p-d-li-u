import sys
try:
    import pptx
    print(f"python-pptx is installed. Version: {pptx.__version__}")
except ImportError:
    print("python-pptx is NOT installed.")

try:
    import PIL
    print(f"Pillow is installed. Version: {PIL.__version__}")
except ImportError:
    print("Pillow is NOT installed.")

print(f"Python version: {sys.version}")
