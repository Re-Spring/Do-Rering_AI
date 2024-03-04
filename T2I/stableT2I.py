import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = "sk-mEarfBLblMX2zZc6eJ3032Is4smpsefMRKjPafXsI6Xw94EA"

makePicture = 10

stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)

class T2I_generator :

    def T2I_generator() :
        answers = stability_api.generate(
            prompt="I'm going to make the main picture of a fairy tale in which a panda is the main character. Please make the picture.",
            seed=4253978046,
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
            print(resp)
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    # 요청하신 API의 안전 필터가 활성화되어 처리할 수 없습니다. 프롬프트를 수정하고 다시 시도해주세요.
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.save("panda3" + ".png")