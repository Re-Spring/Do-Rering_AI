import os
import moviepy.editor as mpy
import librosa
from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips

import traceback

# def generate_video_with_images_and_text(image_paths, audio_paths, output_video_path, fps=24):
#     print(f"Generating video with : {len(image_paths)} images and audio from : {audio_paths}")
#     try:
#         clips = []
#
#         # 이미지 생성
#         for img_path in image_paths:
#             print(f"이미지1111 : {img_path}")
#             clip = mpy.ImageClip(img_path).set_duration(2)  # 예시로 각 이미지를 2초간 보여줌
#             clips.append(clip)
#             print(f"이미지 22222 : {img_path}")
#             # 오디오 생성
#             for audio_path in audio_paths:
#                 print(f"오디오 33333 : {audio_path}")
#                 clip = mpy.AudioFileClip(audio_path).set_duration(2)  # 예시로 각 이미지를 2초간 보여줌
#                 clips.append(clip)
#                 print(f"오디오 444444 : {audio_path}")
#
#         print("뭐가 문제임 ??", clips)
#
#         # 오디오 클립 생성
#         audio_clip = mpy.AudioFileClip(audio_paths[0])
#         print(f"Audio duration : {audio_clip.duration}")
#         # 비디오 클립들을 연결하여 하나의 비디오로 만듦
#         final_clip = mpy.concatenate_videoclips(clips).set_audio(audio_clip)
#         print(f"Final video duration : {final_clip.duration}")
#         # 최종 비디오 파일 저장
#         final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
#         print(f"Video saved to {output_video_path}")
#     except Exception as e:
#         print(f"Error generating video: {e}")
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
            # video = mpy.VideoFileClip(image_path).set_duration(audio_length)
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
            else:
                print("No video clips to concatenate.")
        except Exception as e:
            traceback.print_exc()
            print(f"Error concatenating videos: {e}")
