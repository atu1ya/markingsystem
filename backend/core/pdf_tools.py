from io import BytesIO
from typing import List

from pdf2image import convert_from_bytes
from PIL import Image


def pdf_to_images(pdf_bytes: bytes, dpi: int = 300) -> List[Image.Image]:
    """Convert a single or multi page PDF (as bytes) into a list of Pillow images."""
    images = convert_from_bytes(pdf_bytes, dpi=dpi)
    return images


def image_to_pdf_bytes(image: Image.Image) -> bytes:
    """Convert a single Pillow image into a single page PDF as bytes."""
    buffer = BytesIO()
    image.save(buffer, format="PDF")
    buffer.seek(0)
    return buffer.read()
