import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from text_to_lan import TextToLan  # Assuming this is your custom class

class Imagetranslation:
    def translate():
# Path to Tesseract
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        def get_indic_font(font_size):
            """
            Returns a font object that supports Indian languages (Tamil/Hindi).
            On Windows, 'Nirmala UI' or 'Nirmala.ttf' is standard for Indic scripts.
            """
            try:
                # standard Windows font for Indian languages
                return ImageFont.truetype(r"static\NotoSansTamil-ExtraBold.ttf", font_size) 
            except IOError:
                try:
                    # Fallback for some systems
                    return ImageFont.truetype(r"static\NotoSansTamil-ExtraBold.ttf", font_size)
                except:
                    print("Warning: Indic font not found. Text may appear as boxes.")
                    return ImageFont.load_default()

        def fit_text_to_box(draw, text, box_width, box_height, max_font_size=100):
            font_size = max_font_size
            min_font_size = 10
            
            # Iterate to find the best fit
            while font_size > min_font_size:
                font = get_indic_font(font_size)
                
                # Get text size
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Check if it fits with a small padding
                if text_width <= box_width and text_height <= box_height:
                    return font, font_size, (text_width, text_height)
                    
                font_size -= 2
                
            return get_indic_font(min_font_size), min_font_size, (box_width, box_height)

        # 1. Load Image
        image_path = r"db\image\inp.jpg"
        image = cv2.imread(image_path)

        if image is None:
            print(f"Error: Could not load image at {image_path}")
            exit()

        # 2. Pre-processing for OCR (keep this separate from the display image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Adding a slight blur can sometimes help reduce noise before thresholding
        gray = cv2.medianBlur(gray, 3) 
        _, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 3. Create PIL Image for Drawing (Convert BGR to RGB)
        # We use the ORIGINAL image for the result, not the binary one, to keep colors
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_image)

        # 4. Get Data
        print("Extracting text data...")
        # PSM 11 is 'Sparse text', usually good for labels/scattered words
        data = pytesseract.image_to_data(binary_image, output_type=pytesseract.Output.DICT, config='--psm 11')

        print("Processing and translating...")
        for i in range(len(data['text'])):
            confidence = int(data['conf'][i])
            text = data['text'][i].strip()
            
            # Filter out low confidence, empty text, or tiny artifacts (len < 2)
            if confidence > 50 and len(text) > 1:
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                try:
                    # --- Translate ---
                    # Instantiate your class
                    translator = TextToLan(text) 
                    
                    # Assuming eng_to_tamil returns the string AND sets output_text
                    translated_text = translator.eng_to_tamil() 
                    
                    # Fallback if the method doesn't return the string
                    if not translated_text and hasattr(translator, 'output_text'):
                        translated_text = translator.output_text

                    print(f"Orig: '{text}' -> Tamil: '{translated_text}'")
                    
                    if translated_text:
                        # --- Draw White Box (Background eraser) ---
                        draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
                        
                        # --- Calculate Font ---
                        font, size, (tw, th) = fit_text_to_box(draw, translated_text, w, h)
                        
                        # --- Center Text in Box ---
                        center_x = x + (w - tw) / 2
                        center_y = y + (h - th) / 2
                        
                        draw.text((center_x, center_y), translated_text, fill=(0, 0, 0), font=font)
                        
                except Exception as e:
                    print(f"Error on word '{text}': {e}")

        # 5. Save and Display
        result_image_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        output_path = r"db\image\output_tamil.jpg" # Fixed filename
        cv2.imwrite(output_path, result_image_cv)

        print(f"✓ Saved result to: {output_path}")

        # Resize for display if image is huge
        display_img = result_image_cv.copy()
        if display_img.shape[0] > 800:
            scale = 800 / display_img.shape[0]
            dim = (int(display_img.shape[1] * scale), 800)
            display_img = cv2.resize(display_img, dim)

        cv2.imshow("Translated Result", display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()