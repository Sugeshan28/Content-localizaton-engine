from transformers import VitsModel, AutoTokenizer
import torch
import scipy.io.wavfile
import os

class TextlanToAudio:
    def __init__(self, input_text, target_lang='ta'):
        self.text = input_text
        self.target_lang = target_lang
        
        # MMS-TTS Model Mapping
        self.model_map = {
            'ta': 'facebook/mms-tts-tam',
            'hi': 'facebook/mms-tts-hin',
            'kn': 'facebook/mms-tts-kan',
            'ml': 'facebook/mms-tts-mal',
            'en': 'facebook/mms-tts-eng'
        }

    # ADDED unique_prefix to prevent file overwriting
    def tamil_audio_conv(self, audio_path, unique_prefix="video"):
        # Select the correct AI Model based on target language
        model_name = self.model_map.get(self.target_lang, 'facebook/mms-tts-tam')
        print(f"🎤 Generating Audio for {self.target_lang}...")

        try:
            model = VitsModel.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Input text
            inputs = tokenizer(self.text, return_tensors="pt")
            
            with torch.no_grad():
                output = model(**inputs).waveform
            
            audio = output.squeeze().cpu().numpy()
            
            # Save the file with a UNIQUE name
            # e.g., "db/audio/output_au/12345_ta.wav"
            filename = f"{unique_prefix}_{self.target_lang}.wav"
            output_file = os.path.join(audio_path, filename)
            
            # Save as 16-bit PCM WAV (Standard format for browsers)
            audio_16 = (audio * 32767).astype('int16')
            scipy.io.wavfile.write(output_file, rate=model.config.sampling_rate, data=audio_16)
            
            print(f"✅ Audio saved: {filename}")
            return output_file
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return None