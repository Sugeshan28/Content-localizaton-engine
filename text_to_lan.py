from transformers import pipeline

class TextToLan:
      """Conveting the text to audio"""

      def __init__(self,text:str):
            self.text_input = text
            self.output_text = None
      
      def eng_to_tamil(self):
            """Translates the extracted English text to Tamil and saves it."""
            
            if not self.text_input:
                print("Error: Text has not been extracted yet. Run extract_text() first.")
                return
                
            # Initialize the translation pipeline
            pipe = pipeline("translation", model="facebook/nllb-200-distilled-600M")
            text_to_tam = pipe(self.text_input, src_lang='eng_Latn', tgt_lang='tam_Taml')
            output_text = text_to_tam[0]['translation_text']
            self.output_text = output_text
            with open("tamil_text.txt",'w',encoding='utf-8') as wri:
                  wri.write(output_text)
            print(f"Translated Text: {output_text}")