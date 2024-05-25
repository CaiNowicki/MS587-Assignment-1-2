import os
import fitz  # PyMuPDF
from PIL import Image

def extract_cover_page_as_image(pdf_path, output_folder):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    # Extract the first page
    page = doc.load_page(0)
    
    # Get the page as a pixmap (image)
    pix = page.get_pixmap()

    # Convert the pixmap to a PIL image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Create the output file path
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_folder, f"{base_name}_cover.png")

    # Save the image
    img.save(output_path)
    print(f"Saved cover image for {pdf_path} as {output_path}")

    # Close the document
    doc.close()

def extract_covers_from_folder(folder_path, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            extract_cover_page_as_image(pdf_path, output_folder)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python extract_cover_images.py <pdf_folder_path> <output_folder_path>")
    else:
        pdf_folder_path = sys.argv[1]
        output_folder_path = sys.argv[2]

        if os.path.isdir(pdf_folder_path):
            extract_covers_from_folder(pdf_folder_path, output_folder_path)
        else:
            print(f"{pdf_folder_path} is not a valid directory")
