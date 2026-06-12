import os
from PIL import Image, ImageDraw

def create_placeholder_thumbnail(output_path, theme="blank"):
    # Define standardized widescreen thumbnail size
    width, height = 400, 225
    
    # Masan Palette (from our pptx generator)
    MASAN_RED = (220, 30, 40)
    MASAN_GOLD = (210, 170, 80)
    PURE_WHITE = (255, 255, 255)
    OFF_WHITE = (248, 248, 250)
    TEXT_GRAY = (80, 80, 85)
    BORDER_GRAY = (200, 200, 205)

    # Create core canvas
    img = Image.new("RGB", (width, height), OFF_WHITE)
    draw = ImageDraw.Draw(img)

    if theme == "masan":
        # 1. Paint Corporate Red Header (scaled proportionally)
        draw.rectangle([0, 0, width, 40], fill=MASAN_RED)
        # 2. Paint Accent Gold Thin Line
        draw.rectangle([0, 40, width, 44], fill=MASAN_GOLD)
        
        # 3. Fake Title (White Bar inside Red Header)
        draw.rounded_rectangle([15, 12, 180, 22], radius=3, fill=PURE_WHITE)
        
        # 4. Fake Content Paragraph lines below
        draw.rounded_rectangle([25, 70, 350, 80], radius=3, fill=TEXT_GRAY)
        draw.rounded_rectangle([25, 95, 300, 105], radius=3, fill=TEXT_GRAY)
        draw.rounded_rectangle([25, 120, 330, 130], radius=3, fill=TEXT_GRAY)
        draw.rounded_rectangle([25, 145, 240, 155], radius=3, fill=TEXT_GRAY)
        
        # 5. Gold Footer strip
        draw.rectangle([15, 205, 90, 208], fill=MASAN_GOLD)
        
    else: # theme == "blank"
        # 1. Clear Outer Border to define the slide card
        draw.rectangle([0, 0, width-1, height-1], outline=BORDER_GRAY, width=1)
        
        # 2. Fake Title Line
        draw.rounded_rectangle([25, 25, 220, 40], radius=3, fill=(40, 40, 45))
        
        # 3. Fake Body Paragraph lines
        draw.rounded_rectangle([25, 75, 360, 85], radius=3, fill=TEXT_GRAY)
        draw.rounded_rectangle([25, 100, 340, 110], radius=3, fill=TEXT_GRAY)
        draw.rounded_rectangle([25, 125, 350, 135], radius=3, fill=TEXT_GRAY)
        
    # Save optimized PNG
    img.save(output_path, "PNG")
    print(f"Created visual thumbnail card: {output_path}")

def generate_all_thumbnails(target_dir="templates/previews"):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    blank_path = os.path.join(target_dir, "Default_Blank.png")
    masan_path = os.path.join(target_dir, "Masan_Brand_Template.png")
    
    create_placeholder_thumbnail(blank_path, "blank")
    create_placeholder_thumbnail(masan_path, "masan")

if __name__ == "__main__":
    generate_all_thumbnails()
