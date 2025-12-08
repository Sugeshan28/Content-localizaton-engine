import ffmpeg
import os
from datetime import datetime

class AudioFromVideo:
    """Extracting the audio from Video footage"""

    def __init__(self, video, audio_path="db/audio/eng_audio"):
        self.video_file = video
        self.audio_op_path = audio_path
        save_name = os.path.basename(video)
        self.only_name = os.path.splitext(save_name)[0]
        self.timestamp = datetime.now().strftime("%d%m%Y_%H.%M")
        self.output_name = os.path.join(self.audio_op_path, f"{self.only_name}_{self.timestamp}.mp3")

    def extracting_audio_eng(self):
        """Extract audio from video file"""
        # Ensure output directory exists
        os.makedirs(self.audio_op_path, exist_ok=True)

        input_file = ffmpeg.input(self.video_file)
        audio_file = input_file.audio
        output_name = self.output_name

        try:
            ffmpeg.output(audio_file, output_name, acodec='libmp3lame').run(
                overwrite_output=True,
                capture_stderr=True
            )
            print(f"Audio extracted to: {output_name}")
            return output_name

        except ffmpeg.Error as e:
            print(f"The error in ffmpeg is {e.stderr.decode()}")
            raise