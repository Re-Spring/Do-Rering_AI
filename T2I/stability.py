#@title <a name="Step 2"><font color="#FFFFFF">2. Set up our environment variables and API Key.</font></a>

import getpass, os

# Our Host URL should not be prepended with "https" nor should it have a trailing slash.
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

# Sign up for an account at the following link to get an API Key.
# https://platform.stability.ai/

# Click on the following link once you have created an account to be taken to your API Key.
# https://platform.stability.ai/account/keys

# Paste your API Key below after running this cell.

os.environ['STABILITY_KEY'] = getpass.getpass('Enter your API Key')

#@title <a name="Step 3"><font color="#FFFFFF">3. Import additional dependencies and establish our connection to the API.</font></a>

import cv2
import glob
import io
import os
import getpass
import warnings
from IPython.display import display
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

# API 연결 설정
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)


# 이미지 생성 및 저장 경로 설정
## 폴더 있음?
image_save_folder = 'C:/Users/USER/openai_ex/images'

# 이미지 생성
answers = stability_api.generate(
    prompt="draw colorful woman elf",
    seed=4253978046,
    steps=50,
    cfg_scale=8.0,
    width=1024,
    height=1024,
    samples=1,
    sampler=generation.SAMPLER_K_DPMPP_2M,
)

# 생성된 이미지 저장
for i, resp in enumerate(answers):
    for artifact in resp.artifacts:
        if artifact.type == generation.ARTIFACT_IMAGE:
            img = Image.open(io.BytesIO(artifact.binary))
            # 이미지 저장 경로에 파일 이름 포함
            img_save_path = os.path.join(image_save_folder, f"generated_image_{i+1}.png")
            img.save(img_save_path.replace("\\","/"))
            print(f"Image saved to {img_save_path}")  # 저장된 이미지 경로 출력
# Set up our connection to the API.
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'], # API Key reference.
    verbose=True, # Print debug messages.
    engine="stable-diffusion-xl-1024-v1-0", # Set the engine to use for generation.
    # Check out the following link for a list of available engines: https://platform.stability.ai/docs/features/api-parameters#engine
)

#@title <a name="Step 4"><font color="#FFFFFF">4. Set up initial generation parameters, display image on generation, and safety warning for if the adult content classifier is tripped.</font></a>

# Set up our initial generation parameters.
answers = stability_api.generate(
    prompt="draw fantasy woman elf",
    seed=4253978046, 
    steps=50, 
    cfg_scale=8.0, 
    width=1024,
    height=1024,
    samples=1,
    sampler=generation.SAMPLER_K_DPMPP_2M
)

# Loop through the responses and save each image with a unique filename
for i, resp in enumerate(answers):
    for artifact in resp.artifacts:
        if artifact.type == generation.ARTIFACT_IMAGE:
            img = Image.open(io.BytesIO(artifact.binary))
            img.save(f"generated_image_{i+1}.png")  # Save each image with a unique filename
            display(img)  # Display the image



# 이미지 파일이 저장된 폴더 지정
image_folder = 'C:/Users/USER/openai_ex/images'
# 지정된 폴더에서 모든 이미지 파일 목록 불러오기 (예: PNG 형식)
image_files = sorted(glob.glob(os.path.join(image_folder, '*.png')))

if not image_files:
    print("No images found. Please check the image file path.")
else:
    # 동영상의 프레임 크기 설정 (예: 1920x1080)
    size = (1920, 1080)

    # 동영상 저장을 위한 VideoWriter 객체 생성, fps를 1로 설정
    out = cv2.VideoWriter('output_video_very_slow.avi', cv2.VideoWriter_fourcc(*'DIVX'), 1, size)

    # 이미지 시퀀스를 동영상 파일로 저장, 각 이미지를 10번 반복
    repeat_per_image = 10  # 각 이미지를 10번 반복하여 10초간 보여줌
    for image_file in image_files:
        image = cv2.imread(image_file)
        if image is not None:
            resized_image = cv2.resize(image, size)  # 이미지 크기 조정
            for _ in range(repeat_per_image):
                out.write(resized_image)
        else:
            print(f"Warning: Could not load image {image_file}")

    out.release()  # 동영상 파일 닫기
    print("Video production completed successfully.")