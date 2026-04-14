import easyocr
from better_profanity import profanity

# Initialize EasyOCR reader (only once)
reader = easyocr.Reader(['en'])   # add more languages if needed

# Load default profanity list (can be extended)
profanity.load_censor_words()

def extract_text_from_image(image_path: str) -> str:
    """
    Extract all text from an image using EasyOCR.
    Returns a single string with spaces.
    """
    # detail=0 returns only the text (no bounding boxes or confidence)
    result = reader.readtext(image_path, detail=0)
    if not result:
        return ""
    return " ".join(result)

def moderate_text(text: str) -> dict:
    """
    Check if the extracted text contains profanity.
    Returns:
        - is_appropriate: bool
        - reasons: list
        - extracted_text: the original text
    """
    if not text.strip():
        return {
            "is_appropriate": True,
            "reasons": [],
            "extracted_text": ""
        }
    
    contains_profanity = profanity.contains_profanity(text)
    is_appropriate = not contains_profanity
    reasons = ["Text contains profanity"] if contains_profanity else []
    
    # Optional: also censor the text for safe logging
    # censored_text = profanity.censor(text)
    
    return {
        "is_appropriate": is_appropriate,
        "reasons": reasons,
        "extracted_text": text
    }

def process_text_from_image(image_path: str) -> dict:
    """
    Full pipeline: extract text from image -> moderate that text.
    """
    extracted = extract_text_from_image(image_path)
    return moderate_text(extracted)