import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from pathlib import Path
import random

# 환경 변수 설정
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = "STABILITY_API_KEY"

# Stability AI 클라이언트 초기화
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)


class T2I_generator:
    @staticmethod
    def generator_image(prompt: str) -> (Image.Image, int):
        # 랜덤 시드 값 생성
        seed_number = random.randint(0, 2 ** 32 - 1)

        # 이미지 생성 요청
        answers = stability_api.generate(
            prompt=prompt,
            seed=seed_number,
            steps=50,
            cfg_scale=8.0,
            width=1024,
            height=1024,
            samples=1,
            sampler=generation.SAMPLER_K_DPMPP_2M
        )

        # 생성된 이미지 처리
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    # 안전 필터 경고
                    warnings.warn("Your request activated the API's safety filters. Modify the prompt and try again.")
                elif artifact.type == generation.ARTIFACT_IMAGE:
                    # 이미지 객체 생성 및 반환
                    img = Image.open(io.BytesIO(artifact.binary))
                    return img, seed_number

        # 이미지 생성 실패 시 None 반환
        return None, None


# T2I_generator 클래스 사용 예시
prompt = "I'm going to make the main picture of a fairy tale in which a panda is the main character. Please make the picture."
image, seed = T2I_generator.generator_image(prompt)

if image is not None and seed is not None:
    # 이미지 파일 저장 경로 설정
    image_dir = Path(__file__).resolve().parent.parent / "app/static/text_to_image/images"
    image_dir.mkdir(parents=True, exist_ok=True)

    # 이미지 파일명 설정 및 저장
    img_filename = f"generated_image_{seed}.png"
    img_path = image_dir / img_filename
    image.save(img_path)
    print(f"Image generated with seed {seed} and saved as {img_path}.")
else:
    print("Failed to generate image.")