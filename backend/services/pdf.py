try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from PIL import Image
import io

def rasterize_pdf_to_image(pdf_path: str, output_image_path: str, dpi: int = 300):
    """
    Converts the first page of a PDF to a PNG image.
    Returns the path to the new image or raises an exception.
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF is not installed. Cannot process PDF files.")

    doc = fitz.open(pdf_path)
    if not doc or doc.page_count == 0:
        raise ValueError("Cannot open PDF or PDF is empty.")

    page = doc.load_page(0)  # Load the first page
    
    # Render page to a pixmap (a raster image)
    pix = page.get_pixmap(dpi=dpi)
    
    # Convert pixmap to a PIL Image
    img_data = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_data))
    
    # Save the image
    image.save(output_image_path, "PNG")
    
    doc.close()
    
    return output_image_path
