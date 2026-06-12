import glob, os
from PIL import Image

for f in sorted(glob.glob('*.png') + glob.glob('*.jpg') + glob.glob('*.jpeg')):
    try:
        with Image.open(f) as img:
            print(f"File: {f}, Size: {os.path.getsize(f)} bytes, Format: {img.format}, Mode: {img.mode}, Resolution: {img.size}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
