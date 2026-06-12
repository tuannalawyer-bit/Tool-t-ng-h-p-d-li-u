import fitz # PyMuPDF
import sys

def inspect_pdf(pdf_path):
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    print(f"Total Pages: {len(doc)}")
    
    for i, page in enumerate(doc):
        text = page.get_text()
        rect = page.rect
        print(f"\n--- Page {i+1} (Dimensions: {rect.width}x{rect.height}) ---")
        if text.strip():
            print(f"NATIVE TEXT FOUND:\n{text[:1000]}")
        else:
            print("NO NATIVE TEXT FOUND (Image/Scanned page)")
            # List images on the page
            images = page.get_images()
            print(f"Number of embedded images: {len(images)}")
            for img_idx, img in enumerate(images):
                print(f"  Image {img_idx}: xref={img[0]}, width={img[2]}, height={img[3]}, colorspace={img[5]}")

if __name__ == "__main__":
    inspect_pdf("viber_image_2026-05-17_16-19-19-351.pdf")
