import os
import fitz # PyMuPDF
from PIL import Image, ImageFilter, ImageEnhance

def enhance_pdf():
    print("Initiating Ultra-HD PDF sharpening pipeline...")
    pdf_path = "viber_image_2026-05-17_16-19-19-351.pdf"
    output_path = "WinCommerce_Hoat_Dong_Trong_Tam_2026_HD.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found in the workspace directory!")
        return

    doc = fitz.open(pdf_path)
    enhanced_images = []
    
    for i, page in enumerate(doc):
        print(f"Enhancing Page {i+1} / {len(doc)}...")
        
        # 1. High-fidelity rendering at 4.0x zoom (300 DPI equivalent)
        pix = page.get_pixmap(matrix=fitz.Matrix(4.0, 4.0))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 2. Apply advanced Unsharp Mask to crispen fine text and lines
        img = img.filter(ImageFilter.UnsharpMask(radius=2.5, percent=160, threshold=1))
        
        # 3. Enhance Contrast & Detail Sharpness
        img = ImageEnhance.Contrast(img).enhance(1.05)
        img = ImageEnhance.Sharpness(img).enhance(1.2)
        
        enhanced_images.append(img)
        
    # 4. Compile directly back to a high-quality PDF
    if enhanced_images:
        print(f"Compiling enhanced pages into {output_path}...")
        enhanced_images[0].save(
            output_path, 
            "PDF", 
            save_all=True, 
            append_images=enhanced_images[1:], 
            resolution=300.0,
            quality=95
        )
        print(f"Successfully created enhanced PDF: {output_path}")

if __name__ == "__main__":
    enhance_pdf()
