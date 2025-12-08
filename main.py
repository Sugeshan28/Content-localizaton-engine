from audio_from_video import AudioFromVideo
from text_from_audio import TextFromAudio
from text_to_lan import TextToLan
from textlan_to_audio import TextlanToAudio
import os
from datetime import datetime
from flask import url_for, render_template, Flask, request, send_from_directory, redirect
from werkzeug.utils import secure_filename

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VIDEO_FOLDER = os.path.join(BASE_DIR, 'db', 'video')
AUDIO_FOLDER = os.path.join(BASE_DIR, 'db', 'audio')
AUDIO_ENG_FOLDER = os.path.join(AUDIO_FOLDER, 'eng_audio')
AUDIO_OUTPUT_FOLDER = os.path.join(AUDIO_FOLDER, 'output_au')
TEXT_FOLDER = os.path.join(BASE_DIR, 'db', 'text')
TEXT_ENG_FOLDER = os.path.join(TEXT_FOLDER, 'eng_text')
TEXT_OUTPUT_FOLDER = os.path.join(TEXT_FOLDER, 'output_text')

# Create all necessary directories
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(AUDIO_ENG_FOLDER, exist_ok=True)
os.makedirs(AUDIO_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEXT_ENG_FOLDER, exist_ok=True)
os.makedirs(TEXT_OUTPUT_FOLDER, exist_ok=True)

# Global variables to store current session data
current_video_filename = None
current_title = None
current_description = None
current_source_lang = "en"
current_target_lang = "ta"

app = Flask(__name__)

def recent_audio(audio_path=AUDIO_ENG_FOLDER):
    '''Get the most recently created audio file'''
    files = [os.path.join(audio_path, f)
             for f in os.listdir(audio_path)
             if f.lower().endswith((".mp3", ".wav"))]

    if not files:
        return None

    name = max(files, key=os.path.getmtime)
    print(f"Most recent audio: {name}")
    return name

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return upload()
    return render_template('upload.html')

@app.route("/upload", methods=['POST'])
def upload():
    global current_video_filename, current_title, current_description, current_source_lang, current_target_lang

    if 'videoFile' not in request.files:
        return "No file part", 400

    file = request.files['videoFile']

    if file.filename == '':
        return "No selected file", 400

    if file:
        # Save video file
        filename = secure_filename(file.filename)
        video_path = os.path.join(VIDEO_FOLDER, filename)
        file.save(video_path)
        print(f"Success! Video saved to: {video_path}")

        # Store metadata
        current_video_filename = filename
        current_title = request.form.get('title', 'Untitled')
        current_description = request.form.get('description', '')
        current_source_lang = request.form.get('sourceLanguage', 'en')
        current_target_lang = request.form.get('targetLanguage', 'ta')

        print(f"Title: {current_title}")
        print(f"Description: {current_description}")
        print(f"Source Language: {current_source_lang}")
        print(f"Target Language: {current_target_lang}")

        try:
            # Step 1: Extract audio from video
            print("\n=== Step 1: Extracting audio from video ===")
            ext_audio = AudioFromVideo(video_path, AUDIO_ENG_FOLDER)
            audio_input = ext_audio.extracting_audio_eng()
            print(f"Audio extracted successfully")

            # Step 2: Extract text from audio
            print("\n=== Step 2: Extracting text from audio ===")
            ext_text = TextFromAudio(recent_audio(AUDIO_ENG_FOLDER))
            text_input = ext_text.extracting_text()
            print(f"Text extracted: {text_input[:100]}...")

            # Save English text
            eng_text_path = os.path.join(TEXT_ENG_FOLDER, f"{os.path.splitext(filename)[0]}_eng.txt")
            with open(eng_text_path, 'w', encoding='utf-8') as f:
                f.write(text_input)
            print(f"English text saved to: {eng_text_path}")

            # Step 3: Translate text to target language
            print(f"\n=== Step 3: Translating text to {current_target_lang} ===")
            source_lan = TextToLan(text_input, current_target_lang)
            translated_text = source_lan.eng_to_tamil()
            print(f"Translated text: {translated_text[:100]}...")

            # Save translated text
            translated_text_path = os.path.join(TEXT_OUTPUT_FOLDER, f"{os.path.splitext(filename)[0]}_{current_target_lang}.txt")
            with open(translated_text_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            print(f"Translated text saved to: {translated_text_path}")

            # Step 4: Convert translated text to audio
            print(f"\n=== Step 4: Converting text to audio ===")
            to_audio = TextlanToAudio(translated_text, current_target_lang)
            to_audio.tamil_audio_conv(AUDIO_OUTPUT_FOLDER)
            print("Audio generation completed")

            print("\n=== Processing completed successfully! ===")
            return redirect('/view')

        except Exception as e:
            print(f"Error during processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error processing video: {str(e)}", 500

@app.route('/view')
def view():
    global current_video_filename, current_title, current_description
    return render_template('lmsview.html', 
                         video_filename=current_video_filename,
                         title=current_title or 'Untitled',
                         description=current_description or 'No description')

@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    # Check both eng_audio and output_au folders
    if os.path.exists(os.path.join(AUDIO_ENG_FOLDER, filename)):
        return send_from_directory(AUDIO_ENG_FOLDER, filename)
    elif os.path.exists(os.path.join(AUDIO_OUTPUT_FOLDER, filename)):
        return send_from_directory(AUDIO_OUTPUT_FOLDER, filename)
    else:
        return "Audio file not found", 404

if __name__ == "__main__":
    app.run(debug=True)