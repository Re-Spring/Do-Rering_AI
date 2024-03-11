import os
import moviepy.editor as mpy

def generate_video_with_images_and_text(image_paths, audio_paths, output_video_path, fps=24):
    print(f"Generating video with : {len(image_paths)} images and audio from : {audio_paths}")
    try:
        clips = []

        # 이미지 생성
        for img_path in image_paths:
            print(f"이미지1111 : {img_path}")
            clip = mpy.ImageClip(img_path).set_duration(2)  # 예시로 각 이미지를 2초간 보여줌
            clips.append(clip)
            print(f"이미지 22222 : {img_path}")
            # 오디오 생성
            for audio_path in audio_paths:
                print(f"오디오 33333 : {audio_path}")
                clip = mpy.AudioFileClip(audio_path).set_duration(2)  # 예시로 각 이미지를 2초간 보여줌
                clips.append(clip)
                print(f"오디오 444444 : {audio_path}")

        print("뭐가 문제임 ??", clips)


        # 오디오 클립 생성
        audio_clip = mpy.AudioFileClip(audio_paths[0])
        print(f"Audio duration : {audio_clip.duration}")
        # 비디오 클립들을 연결하여 하나의 비디오로 만듦
        final_clip = mpy.concatenate_videoclips(clips).set_audio(audio_clip)
        print(f"Final video duration : {final_clip.duration}")
        # 최종 비디오 파일 저장
        final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
        print(f"Video saved to {output_video_path}")

        print(f"Video saved to {output_video_path}")
    except Exception as e:
        print(f"Error generating video: {e}")