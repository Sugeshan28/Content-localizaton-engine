import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from text_to_lan import TextToLan

# Tesseract Path (Keep your setting)
# If running on a different server, you might not need this line.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class ImageTranslator:
    def __init__(self, font_path="static/NotoSansTamil-ExtraBold.ttf"):
        self.font_path = font_path

    def get_indic_font(self, font_size):
        try:
            return ImageFont.truetype(self.font_path, font_size) 
        except:
            print("Warning: Indic font not found. Using default.")
            return ImageFont.load_default()

    def fit_text_to_box(self, draw, text, box_width, box_height, max_font_size=100):
        font_size = max_font_size
        min_font_size = 10
        
        while font_size > min_font_size:
            font = self.get_indic_font(font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if text_width <= box_width and text_height <= box_height:
                return font, font_size, (text_width, text_height)
            font_size -= 2
            
        return self.get_indic_font(min_font_size), min_font_size, (box_width, box_height)

    def process(self, image_path, output_path, target_lang='ta'):
        # 1. Load Image
        image = cv2.imread(image_path)
        if image is None: return False

        # 2. Pre-processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3) 
        _, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 3. Convert to PIL for drawing
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_image)

        # 4. OCR Data Extraction
        # psm 11 is good for sparse text
        data = pytesseract.image_to_data(binary_image, output_type=pytesseract.Output.DICT, config='--psm 11')

        found_text = False

        for i in range(len(data['text'])):
            confidence = int(data['conf'][i])
            text = data['text'][i].strip()
            
            if confidence > 40 and len(text) > 1:
                found_text = True
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                
                try:
                    # Translate
                    translator = TextToLan(text, source_lang='en', target_lang=target_lang)
                    translated_text = translator.convert()

                    if translated_text:
                        # Draw White Box (Erase original)
                        draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
                        
                        # Calculate Font & Draw New Text
                        font, size, (tw, th) = self.fit_text_to_box(draw, translated_text, w, h)
                        center_x = x + (w - tw) / 2
                        center_y = y + (h - th) / 2
                        draw.text((center_x, center_y), translated_text, fill=(0, 0, 0), font=font)
                        
                except Exception as e:
                    print(f"Error processing word '{text}': {e}")

        # 5. Save Result
        result_image_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, result_image_cv)
        return True