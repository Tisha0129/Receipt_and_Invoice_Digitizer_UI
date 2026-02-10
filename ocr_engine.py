import pytesseract
from PIL import Image


def extract_text(image: Image.Image):
    """
    Always returns List[str]
    """
    raw_text = pytesseract.image_to_string(image)

    if isinstance(raw_text, str):
        return [line.strip() for line in raw_text.splitlines() if line.strip()]

    # fallback (should never happen)
    return []