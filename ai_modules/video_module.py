import os
import moviepy.editor as mpy
import librosa
from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips

import traceback
class Video_module:
    def __init__(self, video_path, audio_path):
        self.video_path = video_path
        self.audio_path = audio_path

    def get_audio_length(self, audio_name):
        audio_path = os.path.join(str(self.audio_path), audio_name)
        print("inner_audio_path : ", audio_path)

        try:
            y, sr = librosa.load(audio_path, sr=None)
            return librosa.get_duration(y=y, sr=sr)
        except Exception as e:
            print(f"Error getting audio length: {e}")

            return 0

    def generate_video(self, page, title, image_path, audio_path, audio_length):
        output_video_path = os.path.join(str(self.video_path), f"{title}_{page}.mp4")
        fps = 24
        try:
            video_clip = ImageClip(image_path).set_duration(audio_length)
            video_clip = video_clip.set_fps(fps)
            video = video_clip.set_audio(mpy.AudioFileClip(audio_path))
            video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", temp_audiofile=f"{title}_{page}.m4a", remove_temp=True, verbose=False)
        except Exception as e:
            print(f"Error generating video : {e}")

        return output_video_path

    def concatenate_videos(self, video_paths, title):
        output_path = os.path.join(str(self.video_path), f"{title}.mp4")
        clips = []
        fps = 24
        try:
            # 비디오 클립 생성
            for path in video_paths:
                clip = VideoFileClip(path)
                clip = clip.set_fps(fps)
                clips.append(clip)
            # 클립이 비어있는지 확인하고 이어붙이기
            if clips:
                final_clip = concatenate_videoclips(clips)
                final_clip.write_videofile(output_path, codec="libx264", fps=fps)
                return output_path
            else:
                print("No video clips to concatenate.")
        except Exception as e:
            traceback.print_exc()
            print(f"Error concatenating videos: {e}")
