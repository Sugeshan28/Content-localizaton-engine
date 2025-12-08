from transformers import VitsModel, AutoTokenizer
import torch
import scipy.io.wavfile
import os

class TextlanToAudio:
    def __init__(self, input_tam, target_lang='ta'):
        self.tamil_text = input_tam
        self.target_lang = target_lang
        
        # Language model mapping
        self.model_map = {
            'ta': 'facebook/mms-tts-tam',
            'hi': 'facebook/mms-tts-hin',
            'te': 'facebook/mms-tts-tel',
            'bn': 'facebook/mms-tts-ben',
        }
    
    def tamil_audio_conv(self, audio_path):
        model_name = self.model_map.get(self.target_lang, 'facebook/mms-tts-tam')
        
        model = VitsModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        text = self.tamil_text
        inputs = tokenizer(text, return_tensors="pt")
        
        with torch.no_grad():
            output = model(**inputs).waveform
        
        audio = output.squeeze().cpu().numpy()
        audio_16 = (audio*32767).astype('int16')
        
        output_file = os.path.join(audio_path, f"output_audio_{self.target_lang}.wav")
        scipy.io.wavfile.write(output_file, rate=model.config.sampling_rate, data=audio_16)
        
        print(f"Audio saved to: {output_file}")
        return output_file
