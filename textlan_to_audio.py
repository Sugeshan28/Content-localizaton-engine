from transformers import VitsModel, AutoTokenizer
import torch

class TextlanToAudio:
    def __init__(self,input_tam):
        self.tamil_text = input_tam

    def tamil_audio_conv(self,audio_path):
        model = VitsModel.from_pretrained("facebook/mms-tts-tam")
        tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-tam")

        # with open('tamil_text.txt','r',encoding='utf-8') as re:
        #     tamil_text = re.read()

        text = self.tamil_text
        inputs = tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            output = model(**inputs).waveform

        import scipy

        audio = output.squeeze().cpu().numpy()
        audio_16 = (audio*32767).astype('int16')
        scipy.io.wavfile.write(f"db/audio/output_au/output_audio.wav", rate=model.config.sampling_rate, data=audio_16)
