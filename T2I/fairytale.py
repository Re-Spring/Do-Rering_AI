import os
import cv2
import io
import stability_sdk.client as stability_client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image
from pydub import AudioSegment

def process_new_story(new_story_text, new_stories_folder):
    # 새로운 이야기를 저장할 폴더 생성
    new_story_folder = os.path.join(new_stories_folder, f"story_{len(os.listdir(new_stories_folder)) + 1}")
    os.makedirs(new_story_folder, exist_ok=True)

    # 이야기 처리 및 이미지 생성
    generate_images_for_story(new_story_text, new_story_folder)

    # 이미지를 이용하여 동영상 생성
    image_folder = os.path.join(new_story_folder, "generated_images")
    video_save_path = os.path.join(new_story_folder, "story_video.avi")
    generate_video(image_folder, video_save_path)


# FFmpeg 경로 설정
ffmpeg_path = "/path/to/ffmpeg"  # 실제 FFmpeg 바이너리 파일의 경로로 변경해야 합니다.
os.environ["FFMPEG_BINARY"] = ffmpeg_path
AudioSegment.converter = ffmpeg_path

def generate_images_for_story(story_text, story_folder):
    # 이야기 텍스트를 문장으로 분리
    sentences = story_text.strip().split('\n\n')

    # 이미지 저장 경로 설정
    image_save_folder = os.path.join(story_folder, "generated_images")
    os.makedirs(image_save_folder, exist_ok=True)

    # API 설정
    stability_key = os.getenv('STABILITY_KEY')
    if stability_key is None:
        stability_key = input("The 'STABILITY_KEY' environment variable is not set. Please enter your STABILITY_KEY: ")
    stability_api = stability_client.StabilityInference(key=stability_key, verbose=True, engine="stable-diffusion-xl-1024-v1-0")

    # 문장마다 이미지 생성하고 저장
    for i, sentence in enumerate(sentences):
        # 이미지 생성
        responses = stability_api.generate(
            prompt=sentence,
            seed=4253978046,
            steps=50,
            cfg_scale=8.0,
            width=1024,
            height=1024,
            samples=1,
            sampler=generation.SAMPLER_K_DPMPP_2M,
        )

        # 이미지 저장
        for j, response in enumerate(responses):
                for artifact in response.artifacts:
                    if artifact.type == generation.ARTIFACT_IMAGE:
                        img = Image.open(io.BytesIO(artifact.binary))
                        img_save_path = os.path.join(image_save_folder, f"image_paragraph_{i+1}_{j}.png")  # 변경된 부분
                        img.save(img_save_path)
                        print(f"Image saved to {img_save_path}")

    print(f"Images for the story '{story_folder}' generated successfully.")

def generate_video(image_folder, video_save_path):
    # 이미지 파일들 불러오기 (파일명 패턴에 주의하세요)
    image_files = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.png')])

    if not image_files:
        print("No images found. Please check the image file path.")
        return

    # 첫 번째 이미지를 기준으로 프레임 크기 설정
    first_image = cv2.imread(image_files[0])
    height, width, layers = first_image.shape
    size = (width, height)

    # 동영상 저장을 위한 VideoWriter 객체 생성
    out = cv2.VideoWriter(video_save_path, cv2.VideoWriter_fourcc(*'DIVX'), 1, size)

    # 이미지 시퀀스를 동영상 파일로 저장
    repeat_per_image = 10  # 각 이미지를 10번 반복하여 보여줌 (예: FPS가 1일 경우, 10초 동안 보여줌)
    for image_file in image_files:
        image = cv2.imread(image_file)
        for _ in range(repeat_per_image):
            out.write(image)

    out.release()  # 동영상 파일 닫기
    print(f"Video saved to {video_save_path}")

# 새 이야기를 받아와서 처리하는 함수
def process_new_story(new_story_text):
    # 새로운 이야기를 저장할 폴더 생성
    new_story_folder = os.path.join("new_stories", f"story_{len(os.listdir('new_stories')) + 1}")
    os.makedirs(new_story_folder, exist_ok=True)

    # 이야기 처리 및 이미지 생성
    generate_images_for_story(new_story_text, new_story_folder)

    # 이미지를 이용하여 동영상 생성
    image_folder = os.path.join(new_story_folder, "generated_images")
    video_save_path = os.path.join(new_story_folder, "story_video.avi")
    generate_video(image_folder, video_save_path)

# 새로운 이야기를 입력받고 처리
new_story_text = """In the quaint village of Kwon, nestled between rolling hills and whispering streams, there lived a community known for its strong sense of justice. This was a place where fairness was not just a word but a way of life.

At the heart of the village stood a towering oak tree, its branches reaching out like the arms of a guardian. Underneath its sprawling canopy, the villagers would gather each evening to share stories and settle disputes.

One crisp autumn evening, as the sun dipped below the horizon, a commotion stirred in the village square. A group of villagers had gathered, their voices raised in anger. At the center of the crowd stood old Mr. Lee, his weathered face creased with worry."""

process_new_story(new_story_text)
