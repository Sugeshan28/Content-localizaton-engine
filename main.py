import json
import uuid
import os
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, redirect, session
from werkzeug.utils import secure_filename
from image_translator import ImageTranslator
# Import your helper classes
from audio_from_video import AudioFromVideo
from text_from_audio import TextFromAudio
from text_to_lan import TextToLan
from textlan_to_audio import TextlanToAudio
from translations import TRANSLATIONS

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, 'db', 'videos.json') 

IMAGE_FOLDER = os.path.join(BASE_DIR, 'db', 'image')
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Define folders based on your image structure
VIDEO_FOLDER = os.path.join(BASE_DIR, 'db', 'video')
AUDIO_FOLDER = os.path.join(BASE_DIR, 'db', 'audio')
AUDIO_ENG_FOLDER = os.path.join(AUDIO_FOLDER, 'eng_audio')
AUDIO_OUTPUT_FOLDER = os.path.join(AUDIO_FOLDER, 'output_au') # This is where Tamil audio goes

# Create directories if missing
for folder in [VIDEO_FOLDER, AUDIO_ENG_FOLDER, AUDIO_OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Initialize DB
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f: json.dump([], f)

app = Flask(__name__)
app.secret_key = 'hackathon_secret'

# --- HELPER FUNCTIONS ---
def load_videos():
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return []

def save_video_entry(entry):
    videos = load_videos()
    videos.append(entry)
    with open(DB_FILE, 'w') as f: json.dump(videos, f, indent=4)

def get_video_by_id(vid_id):
    videos = load_videos()
    for video in videos:
        if video['id'] == vid_id: return video
    return None

# --- CONTEXT PROCESSOR FOR TRANSLATIONS ---
@app.context_processor
def inject_translations():
    def get_text(key):
        lang = session.get('language', 'en')
        return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    return dict(t=get_text, current_lang=session.get('language', 'en'))

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in TRANSLATIONS: session['language'] = lang_code
    return redirect(request.referrer or '/')

# --- ROUTES ---
@app.route('/')
def home():
    videos = load_videos()
    return render_template('home.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': return upload()
    return render_template('upload.html')

def upload():
    if 'videoFile' not in request.files: return "No file", 400
    file = request.files['videoFile']
    if file.filename == '': return "No file", 400

    if file:
        # 1. Save Video
        filename = secure_filename(file.filename)
        video_path = os.path.join(VIDEO_FOLDER, filename)
        file.save(video_path)

        title = request.form.get('title', 'Untitled')
        desc = request.form.get('description', '')
        source_lang = 'en'
        
        # GENERATE ID
        video_id = str(uuid.uuid4())
        
        try:
            print(f"🎬 Processing Video: {filename}")

            # 2. Extract English Audio
            print("🔊 Extracting Original Audio...")
            ext_audio = AudioFromVideo(video_path, AUDIO_ENG_FOLDER)
            english_audio_path = ext_audio.extracting_audio_eng()

            # 3. Speech to Text (English)
            print("📝 Transcribing to Text...")
            ext_text = TextFromAudio(english_audio_path)
            source_text = ext_text.extracting_text()
            
            content_map = {}
            
            # --- FORCE TAMIL CONVERSION START ---
            print("🔄 Starting Tamil Translation Loop...")
            
            # Define just Tamil for now to speed up your testing
            target_langs = ['ta'] 

            for lang in target_langs:
                lang_data = {}
                
                # A. Translate Text (English -> Tamil)
                print(f"   Translating text to {lang}...")
                translator = TextToLan(source_text, source_lang=source_lang, target_lang=lang)
                translated_text = translator.convert()
                lang_data['text'] = translated_text
                
                # B. Generate Audio (Tamil TTS)
                print(f"   Generating Audio for {lang}...")
                tts = TextlanToAudio(translated_text, target_lang=lang)
                
                # Ensure unique filename using video_id
                # This saves to db/audio/output_au/
                audio_path = tts.tamil_audio_conv(AUDIO_OUTPUT_FOLDER, unique_prefix=video_id)
                
                if audio_path:
                    lang_data['audio_file'] = os.path.basename(audio_path)
                    print(f"   ✅ Saved: {lang_data['audio_file']}")
                else:
                    lang_data['audio_file'] = None
                    print("   ❌ Failed to generate audio")

                content_map[lang] = lang_data
            # --- FORCE TAMIL CONVERSION END ---

            # 4. Save to JSON Database
            new_entry = {
                "id": video_id,
                "title": title,
                "description": desc,
                "original_filename": filename,
                "content_map": content_map,
                "timestamp": datetime.now().strftime("%Y-%m-%d")
            }
            save_video_entry(new_entry)
            
            return redirect('/')

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}", 500

@app.route('/view/<video_id>')
def view_video(video_id):
    video = get_video_by_id(video_id)
    if not video: return "Video not found", 404
    
    # Debug print to check if content_map exists
    print(f"View content map: {video.get('content_map')}")
    
    return render_template('lmsview.html', 
                           video=video,  
                           content_map=json.dumps(video.get('content_map', {})))

@app.route('/video/<path:filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    # Try serving from output_au (Tamil audio)
    if os.path.exists(os.path.join(AUDIO_OUTPUT_FOLDER, filename)):
        return send_from_directory(AUDIO_OUTPUT_FOLDER, filename)
    # Fallback to eng_audio (English audio)
    return send_from_directory(AUDIO_ENG_FOLDER, filename)


@app.route('/image_translate', methods=['GET', 'POST'])
def image_translate():
    processed_image = None
    original_image = None
    
    if request.method == 'POST':
        if 'imageFile' not in request.files: return "No file", 400
        file = request.files['imageFile']
        
        if file:
            # 1. Save Input
            filename = secure_filename(file.filename)
            input_path = os.path.join(IMAGE_FOLDER, filename)
            file.save(input_path)
            
            # 2. Define Output Filename
            output_filename = f"translated_{filename}"
            output_path = os.path.join(IMAGE_FOLDER, output_filename)
            
            # 3. Run Your CV Code
            # Ensure the font file exists in static folder!
            translator = ImageTranslator(font_path=os.path.join(BASE_DIR, 'static', 'NotoSansTamil-ExtraBold.ttf'))
            success = translator.process(input_path, output_path, target_lang='ta')
            
            if success:
                processed_image = output_filename
                original_image = filename
    
    return render_template('image_translate.html', 
                         original=original_image, 
                         processed=processed_image)

@app.route('/image/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)