from transformers import pipeline

class TextToLan:
    """Converting the text to different languages"""

    def __init__(self, text: str, target_lang: str = 'ta'):
        self.text_input = text
        self.target_lang = target_lang
        self.output_text = None

        # Language code mapping for NLLB model
        self.lang_map = {
            'ta': 'tam_Taml',  # Tamil
            'hi': 'hin_Deva',  # Hindi
            'bn': 'ben_Beng',  # Bengali
            'te': 'tel_Telu',  # Telugu
            'mr': 'mar_Deva',  # Marathi
            'gu': 'guj_Gujr',  # Gujarati
            'kn': 'kan_Knda',  # Kannada
            'ml': 'mal_Mlym',  # Malayalam
            'pa': 'pan_Guru',  # Punjabi
            'ur': 'urd_Arab',  # Urdu
            'as': 'asm_Beng',  # Assamese
            'or': 'ory_Orya',  # Odia
        }

    def eng_to_tamil(self):
        """Translates the extracted English text to target language and saves it."""
        if not self.text_input:
            print("Error: Text has not been extracted yet.")
            return

        # Get target language code
        tgt_lang_code = self.lang_map.get(self.target_lang, 'tam_Taml')

        # Initialize the translation pipeline
        pipe = pipeline("translation", model="facebook/nllb-200-distilled-600M")

        try:
            text_translated = pipe(self.text_input, src_lang='eng_Latn', tgt_lang=tgt_lang_code)
            output_text = text_translated[0]['translation_text']
            self.output_text = output_text

            print(f"Translated Text ({self.target_lang}): {output_text[:100]}...")
            return output_text

        except Exception as e:
            print(f"Translation error: {str(e)}")
            return self.text_input  # Return original text if translation fails