from transformers import pipeline

class TextToLan:
    def __init__(self, text: str, source_lang: str = 'en', target_lang: str = 'ta'):
        self.text_input = text
        self.source_lang = source_lang
        self.target_lang = target_lang

        # NLLB-200 Language Codes
        self.lang_map = {
            'en': 'eng_Latn',  # English
            'ta': 'tam_Taml',  # Tamil
            'hi': 'hin_Deva',  # Hindi
            'te': 'tel_Telu',  # Telugu
            'kn': 'kan_Knda',  # Kannada
            'ml': 'mal_Mlym',  # Malayalam
            'bn': 'ben_Beng',  # Bengali
            'gu': 'guj_Gujr',  # Gujarati
            'mr': 'mar_Deva',  # Marathi
        }

    def convert(self):
        if not self.text_input: 
            return ""

        # Get codes (Default to English/Tamil if missing)
        src_code = self.lang_map.get(self.source_lang, 'eng_Latn')
        tgt_code = self.lang_map.get(self.target_lang, 'tam_Taml')

        print(f"🔀 Translating from {src_code} to {tgt_code}...")

        try:
            # Load Translation Model
            pipe = pipeline("translation", model="facebook/nllb-200-distilled-600M")
            
            # IMPORTANT: The model fails on long text. We must split it into chunks.
            chunks = self._chunk_text(self.text_input)
            translated_parts = []

            for chunk in chunks:
                if chunk.strip():
                    result = pipe(chunk, src_lang=src_code, tgt_lang=tgt_code)
                    translated_parts.append(result[0]['translation_text'])
            
            # Combine all translated parts
            final_text = " ".join(translated_parts)
            return final_text

        except Exception as e:
            print(f"Translation Error: {e}")
            # Fallback: Return original text so the code doesn't crash
            return self.text_input

    def _chunk_text(self, text, max_len=400):
        """
        Splits long text into smaller chunks to prevent AI model crash.
        Splits by periods (.) to keep sentences intact.
        """
        sentences = text.split('.')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_len:
                current_chunk += sentence + "."
            else:
                chunks.append(current_chunk)
                current_chunk = sentence + "."
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    # Alias for backward compatibility with your older code calls
    def eng_to_tamil(self):
        return self.convert()