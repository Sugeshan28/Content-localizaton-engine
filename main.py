from audio_from_video import AudioFromVideo
from text_from_audio import TextFromAudio
from text_to_lan import TextToLan
from textlan_to_audio import TextlanToAudio
import os
from datetime import datetime
from flask import url_for,render_template,Flask

#FUNCTION FOR LATEST AUDIO
def recent_audio(audio_path = 'db/audio'):
    files = [os.path.join(audio_path,f)
             for f in os.listdir(audio_path)
             if f.lower().endswith((".mp3",".wav"))
             ]
    if not files:
        return None
    
    name = max(files,key = os.path.getmtime)
    print(f"File name {name}")
    return name

#NAMING FUNCTION
uplo = None
def naming_file():
    if uplo:
        curr_file_name = uplo
        timestamp = datetime.now().strftime(f"%m%d%y|%H.%M")
        name = f"{timestamp}_{curr_file_name}"

VIDEO_FOLDER = r"db\video\vid4.mp4"
AUDIO_FOLDER = "db/audio"

#AUDIOFROMVIDEO
ext_audio = AudioFromVideo(VIDEO_FOLDER,AUDIO_FOLDER)
audio_input = ext_audio.extracting_audio()
#TEXT TO AUDIO
ext_text = TextFromAudio(recent_audio())
text_input = ext_text.extracting_text()
print(f"Text output{ext_text.text}")
#TEXT TO LANGUAGE
source_lan = TextToLan(ext_text.text)
translated_text = source_lan.eng_to_tamil()
print(translated_text)

to_audio = TextlanToAudio(source_lan.output_text)
to_audio.tamil_audio_conv(recent_audio())

app = Flask(__name__)

@app.route('/')
def upload_page():
    return render_template('upload.html')

if __name__ == "__main__":
    app.run(debug=True)