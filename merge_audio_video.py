import ffmpeg
import os

def merge_video_with_translated_audio(video_path, translated_audio_path, output_path):
    """
    Merge video with translated audio, adjusting audio speed to match video duration
    """
    try:
        # Get video duration
        probe = ffmpeg.probe(video_path)
        video_duration = float(probe['format']['duration'])

        # Get audio duration
        audio_probe = ffmpeg.probe(translated_audio_path)
        audio_duration = float(audio_probe['format']['duration'])

        print(f"Video duration: {video_duration}s")
        print(f"Audio duration: {audio_duration}s")

        # Calculate speed adjustment factor
        speed_factor = audio_duration / video_duration

        # Load video without audio
        video = ffmpeg.input(video_path).video

        # Load translated audio and adjust speed
        audio = ffmpeg.input(translated_audio_path).audio

        # Adjust audio speed (tempo) to match video duration
        # atempo filter accepts values between 0.5 and 2.0
        if speed_factor > 2.0:
            # Need to chain multiple atempo filters
            audio = audio.filter('atempo', 2.0)
            remaining = speed_factor / 2.0
            while remaining > 2.0:
                audio = audio.filter('atempo', 2.0)
                remaining = remaining / 2.0
            audio = audio.filter('atempo', remaining)
        elif speed_factor < 0.5:
            # Slow down in stages
            audio = audio.filter('atempo', 0.5)
            remaining = speed_factor / 0.5
            while remaining < 0.5:
                audio = audio.filter('atempo', 0.5)
                remaining = remaining / 0.5
            audio = audio.filter('atempo', remaining)
        else:
            audio = audio.filter('atempo', speed_factor)

        # Merge video and adjusted audio
        output = ffmpeg.output(video, audio, output_path, 
                              vcodec='copy', acodec='aac', 
                              strict='experimental')

        # Run the merge
        ffmpeg.run(output, overwrite_output=True, capture_stderr=True)

        print(f"✅ Successfully merged video with translated audio!")
        print(f"Output saved to: {output_path}")
        return output_path

    except ffmpeg.Error as e:
        print(f"Error merging video and audio: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise
