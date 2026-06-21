from transformers import pipeline
import torch
import gc

class TextToLan:
    def __init__(self, text=None, source_lang='en', target_lang='ta', model_pipeline=None):
        """
        Initialize the translator.
        Can be used in two ways:
        1. TextToLan(text, source_lang='en', target_lang='ta') - for immediate translation
        2. TextToLan() - create instance, then call translate() method
        """
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.pipe = model_pipeline
        
        # NLLB-200 Language Codes
        self.lang_map = {
            'en': 'eng_Latn',
            'ta': 'tam_Taml',
            'hi': 'hin_Deva',
            'kn': 'kan_Knda',
            'ml': 'mal_Mlym',
            'te': 'tel_Telu',
        }

    def load_model(self):
        """Loads the model only if it wasn't passed in"""
        if self.pipe is None:
            print("⏳ Loading Translation Model (NLLB)...")
            device = 0 if torch.cuda.is_available() else -1
            self.pipe = pipeline("translation", model="facebook/nllb-200-distilled-600M", device=device)

    def convert(self):
        """
        Translate text using parameters from __init__
        Used for: translator = TextToLan(text, source_lang='en', target_lang='ta')
                  result = translator.convert()
        """
        if not self.text:
            return ""
        
        return self.translate(self.text, self.source_lang, self.target_lang)

    def translate(self, text, source_lang, target_lang):
        """
        Translate text with explicit parameters
        Used for: translator = TextToLan()
                  result = translator.translate(text, 'en', 'ta')
        """
        if not text:
            return ""
        
        if self.pipe is None:
            self.load_model()

        src_code = self.lang_map.get(source_lang, 'eng_Latn')
        tgt_code = self.lang_map.get(target_lang, 'tam_Taml')

        try:
            # Chunking logic to prevent crash on long text
            chunks = self._chunk_text(text)
            translated_parts = []

            for chunk in chunks:
                if chunk.strip():
                    # Pass src_lang and tgt_lang to the pipeline
                    result = self.pipe(chunk, src_lang=src_code, tgt_lang=tgt_code)
                    translated_parts.append(result[0]['translation_text'])
            
            return " ".join(translated_parts)

        except Exception as e:
            print(f"Translation Error: {e}")
            return text

    def _chunk_text(self, text, max_len=400):
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
