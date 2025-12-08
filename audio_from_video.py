import ffmpeg
import os
from datetime import datetime

class AudioFromVideo:
    """Extracting the audio from Video footage"""

    def __init__(self,video,audio_path= r"db\audio"):
        self.video_file = video
        self.audio_op_path = audio_path
        save_name = os.path.basename(video)
        self.only_name = os.path.splitext(save_name)[0]
        self.timestamp = datetime.now().strftime(f"%d%m%Y_%H.%M")
        self.output_name = os.path.join(self.audio_op_path,f"{self.only_name}_{self.timestamp}.mp3")
    
    def extracting_audio_eng(self,audio_path = r"db\audio\eng_audio"):
        input_file= ffmpeg.input(self.video_file)
        audio_file = input_file.audio
        output_name = os.path.join(self.audio_op_path,f"{self.only_name}_{self.timestamp}.mp3")
        try:
            ffmpeg.output(audio_file,output_name,acodec='libmp3lame').run( 
                overwrite_output=True,
                capture_stderr =True)
        except ffmpeg.Error as e:
            print(f"The error in ffmpeg is {e.stderr.decode()}")
