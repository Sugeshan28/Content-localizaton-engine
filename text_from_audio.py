from transformers import pipeline
import whisper

class TextFromAudio:
    """Extracting the text from the audio samples"""

    def __init__(self,audio_path):
        self.audio_path = audio_path
        # self.text_path = text_path
        self.model = whisper.load_model('base')
        self.text = None
    
    def extracting_text(self):
        result = self.model.transcribe(self.audio_path,fp16=False)
        self.text = result['text']
        # with open('new.txt','w') as wri:
        #     wri.write(self.text)
        return self.text
       
