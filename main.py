from audio_from_video import AudioFromVideo
from text_from_audio import TextFromAudio
from text_to_lan import TextToLan
from textlan_to_audio import TextlanToAudio
import os
from datetime import datetime
from flask import url_for,render_template,Flask,request
from werkzeug.utils import secure_filename

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

# #NAMING FUNCTION
# uplo = None
# def naming_file():
#     if uplo:
#         curr_file_name = uplo
#         timestamp = datetime.now().strftime(f"%m%d%y|%H.%M")
#         name = f"{timestamp}_{curr_file_name}"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VIDEO_FOLDER = os.path.join(BASE_DIR, 'db', 'video')
AUDIO_FOLDER = os.path.join(BASE_DIR, 'db', 'audio')

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def audiofromvideo(Videofolder):
    #AUDIOFROMVIDEO
    ext_audio = AudioFromVideo(Videofolder,AUDIO_FOLDER)
    audio_input = ext_audio.extracting_audio_eng()
    return audio_input

def texttoaudio():
    #TEXT TO AUDIO
    ext_text = TextFromAudio(recent_audio())
    text_input = ext_text.extracting_text()
    print(f"Text output{ext_text.text}")
    return ext_text.text

def texttolanguage(ext_text):
    #TEXT TO LANGUAGE
    source_lan = TextToLan(ext_text)
    translated_text = source_lan.eng_to_tamil()
    print(translated_text)
    return source_lan.output_text

def textlantoaudio(source_lan):
    to_audio = TextlanToAudio(source_lan)
    to_audio.tamil_audio_conv(recent_audio())

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

title = None
description = None

@app.route("/", methods=['POST'])
def upload():
    global title,description
    if 'videoFile' not in request.files:
        return "No file part"
    file = request.files['videoFile']
    if file.filename == '':
        return "No selected file"

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(VIDEO_FOLDER,filename))
        print(f"Success! Video saved to: {VIDEO_FOLDER}/{filename}")

    #getting title
    title_name = request.form.get('title')  
    title = title_name

    description_title = request.form.get('description')
    description = description_title

    print(f"the title {title}")
    print(f"the description {description}")

    #initiating flow
    audiofromvideo(f"{VIDEO_FOLDER}/{filename}")
    textlantoaudio(texttolanguage(texttoaudio()))

if __name__ == "__main__":
    app.run(debug=True)