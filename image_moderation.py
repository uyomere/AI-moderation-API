from nudenet import NudeDetector

detector = NudeDetector()

# Classes that are sexually explicit or nude
EXPLICIT_CLASSES = {
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "BUTTOCKS_EXPOSED",
    "ANUS_EXPOSED",
    "BREAST_EXPOSED",       # generic
    "GENITALIA_EXPOSED",    # generic
}

def moderate_image_content(image_path: str) -> dict:
    detections = detector.detect(image_path)
    threshold = 0.6

    # Only flag detections that are both above threshold AND in the explicit list
    flagged = [
        d for d in detections
        if d['score'] >= threshold and d['class'] in EXPLICIT_CLASSES
    ]

    is_appropriate = len(flagged) == 0
    reasons = [f"{d['class']} (confidence: {d['score']:.2f})" for d in flagged]

    return {
        "is_appropriate": is_appropriate,
        "reasons": reasons,
        "detection_count": len(flagged)
    }