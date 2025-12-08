import ffmpeg
import os
from datetime import datetime

class AudioFromVideo:
    """Extracting the audio from Video footage"""

    def __init__(self,video,audio_path= r"db\audio"):
        self.video_file = video
        self.audio_op_path = audio_path
        save_name = os.path.basename(video)
        only_name = os.path.splitext(save_name)[0]
        timestamp = datetime.now().strftime(f"%d%m%Y_%H.%M")
        self.output_name = os.path.join(self.audio_op_path,f"{only_name}_{timestamp}.mp3")
    
    def extracting_audio(self):
        input_file= ffmpeg.input(self.video_file)
        audio_file = input_file.audio
        try:
            ffmpeg.output(audio_file,self.output_name,acodec='libmp3lame').run( 
                overwrite_output=True,
                capture_stderr =True)
        except ffmpeg.Error as e:
            print(f"The error in ffmpeg is {e.stderr.decode()}")
