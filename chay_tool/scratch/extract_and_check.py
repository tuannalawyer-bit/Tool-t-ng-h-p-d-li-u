import fitz # PyMuPDF
import os

def extract_pdf_images(pdf_path):
    print(f"Extracting images from: {pdf_path}")
    doc = fitz.open(pdf_path)
    os.makedirs("scratch", exist_ok=True)
    
    for i, page in enumerate(doc):
        image_list = page.get_images(full=True)
        print(f"Page {i+1} has {len(image_list)} images")
        for img_idx, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            filename = f"scratch/viber_page_{i+1}.{image_ext}"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"  Saved: {filename} (Ext: {image_ext}, Size: {len(image_bytes)} bytes)")

if __name__ == "__main__":
    extract_pdf_images("viber_image_2026-05-17_16-19-19-351.pdf")
