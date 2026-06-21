import ffmpeg
import os

class AudioSync:
    def __init__(self, original_video_path, generated_audio_path):
        self.video_path = original_video_path
        self.audio_path = generated_audio_path

    def get_duration(self, filepath):
        try:
            probe = ffmpeg.probe(filepath)
            return float(probe['format']['duration'])
        except Exception as e:
            print(f"Error probing {filepath}: {e}")
            return 0.0

    def sync_audio(self, output_path):
        """Stretches or compresses audio to match video duration exactly"""
        video_dur = self.get_duration(self.video_path)
        audio_dur = self.get_duration(self.audio_path)

        if video_dur == 0 or audio_dur == 0:
            print("⚠️ Duration check failed. Using original audio length.")
            return self.audio_path # Return original if check fails

        # Calculate speed factor
        speed_factor = audio_dur / video_dur
        
        # Clamp speed to avoid errors (ffmpeg limit is usually 0.5 to 2.0)
        # If it's extreme, we handle it by chaining filters (simplified here to just limit)
        if speed_factor < 0.5: speed_factor = 0.5
        if speed_factor > 2.0: speed_factor = 2.0

        print(f"⏱️ Syncing: Video {video_dur}s | Audio {audio_dur}s | Speed Factor: {speed_factor:.2f}x")

        try:
            # atempo filter changes speed without changing pitch
            stream = ffmpeg.input(self.audio_path)
            stream = stream.filter('atempo', speed_factor)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
            return output_path
        except ffmpeg.Error as e:
            print(f"FFmpeg Sync Error: {e.stderr.decode()}")
            return self.audio_path