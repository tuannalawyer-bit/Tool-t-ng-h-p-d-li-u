import os
import shutil
from PIL import Image

brain_dir = r"C:\Users\tuanna13\.gemini\antigravity\brain\a4e09c09-3b09-4ea1-8464-8e6fb2e6795d"
dest_dir = r"d:\Dự án AI\chay_tool\scratch"

# Let's list all media files in the brain folder
media_files = [f for f in os.listdir(brain_dir) if f.startswith("media__") and f.endswith(".jpg")]
print("Found media files:", media_files)

# Let's print their details
for f in sorted(media_files):
    path = os.path.join(brain_dir, f)
    with Image.open(path) as img:
        print(f"File: {f}, Resolution: {img.size}")
