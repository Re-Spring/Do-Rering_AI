import io
import warnings
from pathlib import Path  # 파일 경로를 다루기 위한 모듈
import uuid
import random  # 랜덤 모듈 추가
from PIL import Image
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import sys
sys.path.append('..')

# T2I.stableT2I 모듈에서 T2I_generator 클래스와 stability_api 인스턴스를 임포트
from T2I.stableT2I import T2I_generator, stability_api

# T2I 생성을 통해 이미지와 시드 값을 얻습니다.
t2i_image, t2i_seed = T2I_generator.generator_image("A magical forest with unicorns and fairies")  # 메서드 이름 수정

if t2i_image is not None and t2i_seed is not None:
    # I2I 변환을 위한 초기 이미지로 T2I에서 생성된 이미지를 사용합니다.
    answers2 = stability_api.generate(
        prompt="I'm going to make the main picture of a fairy tale in which a panda is the main character. Please make the picture.",
        init_image=t2i_image,  # T2I에서 생성된 이미지를 초기 이미지로 사용
        seed=t2i_seed,
        steps=50,
        cfg_scale=8.0,
        width=1024,
        height=1024,
        sampler=generation.SAMPLER_K_DPMPP_2M
    )

    for resp in answers2:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn("Your request activated the API's safety filters and could not be processed. Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img2 = Image.open(io.BytesIO(artifact.binary))
                # 이미지 저장 경로 설정
                image_dir = Path(__file__).resolve().parent.parent / "static/T2I/images"
                image_dir.mkdir(parents=True, exist_ok=True)

                # UUID를 이용하여 이미지 파일명 설정
                img_filename = f"{uuid.uuid4()}.png"
                img_path = image_dir / img_filename

                img2.save(img_path)  # 수정된 부분: img2 변수를 사용하여 이미지 파일 저장
                print(f"Image saved to {img_path}")  # 이미지 파일 경로 출력
