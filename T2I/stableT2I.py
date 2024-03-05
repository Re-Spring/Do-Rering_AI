import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from pathlib import Path  # 파일 경로를 다루기 위한 모듈
import uuid
import random  # 랜덤 모듈 추가

os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = "sk-mEarfBLblMX2zZc6eJ3032Is4smpsefMRKjPafXsI6Xw94EA"

makePicture = 10

stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)

class T2I_generator :
    @staticmethod
    def generator_image(prompt: str) -> (Image, int):
        # 0과 2^32-1 사이의 랜덤한 정수를 seed값을 생성합니다.
        seed_number = random.randint(0, 2**32-1)
        prompt = "I'm going to make the main picture of a fairy tale in which a panda is the main character. Please make the picture."
        answers = stability_api.generate(
            prompt=prompt,
            seed=seed_number,
            # seed=1234567890,
            steps=50, # 이미지 생성에 수행된 추론 단계의 양. 기본값은 30입니다.
            cfg_scale=8.0,
            # 프롬프트에 맞게 세대가 얼마나 강력하게 안내되는지에 영향을 미칩니다.
            # 이 값을 더 높게 설정하면 프롬프트와 일치하는 강도가 높아집니다.
            # 지정하지 않은 경우 기본값은 7.0입니다.
            width=1024,
            height=1024,
            samples=1,
            sampler=generation.SAMPLER_K_DPMPP_2M
            # 우리 세대의 노이즈를 제거할 샘플러를 선택하십시오.
            # 지정하지 않은 경우 기본값은 k_dpmpp_2m입니다. 클립 안내는 조상 샘플러만 지원합니다.
            # # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
        )

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed. Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))

                    # # 이미지 저장 경로 설정
                    # image_dir = Path(__file__).resolve().parent.parent / "static/text_to_image/images"  # 이미지 저장 경로 설정
                    # image_dir.mkdir(parents=True, exist_ok=True)  # 해당 경로가 없다면 생성합니다.
                    #
                    # #UUID를 이용하여 이미지 파일명 설정
                    # img_filename = f"{uuid.uuid4()}.png"
                    # img_path = image_dir / img_filename  # 이미지 파일명 설정
                    #
                    # img.save(img_path)  # 이미지 파일 저장
                    # print(f"Image saved to {img_path}") # 이미지 파일 경로 출력
                    # 이미지 저장은 여기에서 생략하고, 이미지 객체롸 시드 번호를 반환 합니다.
                    return img, seed_number # 이미지 객체와 시드 번호 반환
        return None, None # 이미지 생성 실패 시 None 반환
# T2I_generator.generator_image()
