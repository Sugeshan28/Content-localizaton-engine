import whisper
import torch

class TextFromAudio:
    def __init__(self, audio_path, language='en'):
        self.audio_path = audio_path
        self.language = language
        # 'tiny' is 32x faster than 'base'. Use 'small' if you need better accuracy.
        self.model_name = 'tiny' 
        self.model = None

    def extracting_text(self):
        # Load model only when needed
        if self.model is None:
            print(f" Loading Whisper ({self.model_name})...")
            self.model = whisper.load_model(self.model_name)
        
        options = {"language": self.language}
        
        # Enable fp16 if GPU is available (Much faster)
        use_fp16 = torch.cuda.is_available()
        
        print(f" Listening ({self.language})...")
        result = self.model.transcribe(self.audio_path, **options, fp16=use_fp16)
        
        return result['text']