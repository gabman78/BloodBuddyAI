from paddleocr import PaddleOCR  # type: ignore
from PIL import Image, ImageEnhance
import numpy as np
np.int = int
import cv2  # type: ignore
import difflib
from io import BytesIO

UNIT_CATALOG = ["mg/dl", "µg/dl", "mEq/L", "mmol/L", "U/L", "ng/mL", "pg/mL"]

def enhance_image_for_ocr_pil(img_pil, scale_factor=1.5):
    w, h = img_pil.size
    img = img_pil.resize((int(w * scale_factor), int(h * scale_factor)), Image.LANCZOS)
    gray = np.array(img.convert("L"))
    gray = cv2.fastNlMeansDenoising(gray, h=20)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    blurred = cv2.GaussianBlur(closed, (3, 3), sigmaX=1)
    sharpened = cv2.addWeighted(closed, 1.2, blurred, -0.2, 0)
    pil_img = Image.fromarray(sharpened)
    enhancer = ImageEnhance.Contrast(pil_img)
    final_img = enhancer.enhance(1.3)
    return final_img

def normalize_unit(raw_unit, catalog=UNIT_CATALOG, cutoff=0.4):
    u = raw_unit.strip().lower()
    match = difflib.get_close_matches(u, catalog, n=1, cutoff=cutoff)
    return match[0] if match else raw_unit.strip()

def normalize_output_units(raw_text):
    normalized_lines = []
    for line in raw_text.split("\n"):
        if not line.strip():
            continue
        cols = [c.strip() for c in line.split("|")]
        if len(cols) >= 3:
            cols[2] = normalize_unit(cols[2])
        normalized_lines.append(" | ".join(cols))
    return "\n".join(normalized_lines)

def perform_ocr(image_input):
    """Esegue OCR e restituisce il testo grezzo raggruppato per righe."""
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='it')
        # 🔄 Conversione tipo input
        if isinstance(image_input, BytesIO):
            image_input = Image.open(image_input)
        if isinstance(image_input, Image.Image):
            image_input = np.array(image_input.convert("RGB"))

        results = ocr.ocr(image_input)
        if not results or results[0] is None:
            print("⚠️ OCR non ha trovato testo.")
            return ""
        boxes_texts = [(det[0], det[1][0]) for det in results[0]]
        
        def get_center_y(box):
            return np.mean([point[1] for point in box])

        tolleranza_y = 15
        righe = []
        for box, text in sorted(boxes_texts, key=lambda x: get_center_y(x[0])):
            trovato = False
            center_y = get_center_y(box)
            for riga in righe:
                if abs(riga['center_y'] - center_y) < tolleranza_y:
                    riga['elementi'].append((box, text))
                    trovato = True
                    break
            if not trovato:
                righe.append({'center_y': center_y, 'elementi': [(box, text)]})
        output = ""
        for riga in righe:
            elementi = sorted(riga['elementi'], key=lambda x: min(p[0] for p in x[0]))
            texts = [text for _, text in elementi]
            output += " | ".join(texts) + "\n"

        print("🧪 OCR terminato con successo.")
        return output.strip()
    
    except Exception as e:
        print("❌ Errore durante l'esecuzione dell'OCR:", e)
        return ""

