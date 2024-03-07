import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일에서 환경 변수를 불러오는 부분입니다.
load_dotenv()

# Stability AI 서버 정보와 API 키를 환경 변수에서 설정합니다.
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
STABILITY_KEY = os.environ.get("STABILITY_KEY")

# 경로 설정 및 필요한 디렉터리 생성
base_dir = Path(__file__).resolve().parent / "static/text_to_image"
image_path = str(base_dir/"images")
# 이미지 디렉토리가 존재하지 않으면 생성
if not image_path.exists():
    image_path.mkdir(parents=True)
image_font_path = str(base_dir / "font" / "SpoqaHanSansNeo-Light.ttf")

# 임시 프롬프트

korean_prompts = [
    "옛날, 작은 마을 가장자리에 신비로운 숲이 있었습니다.",
    "이 숲은 새들이 노래하는 소리와 나무들이 춤추는 소리로 가득 찼습니다.",
    "하지만, 마을 사람들은 숲이 너무 깊고 미로 같다고 생각해서 아무도 감히 깊은 곳으로 모험하지 못했습니다.",
    "아이들은 항상 숲이 어떤 비밀을 품고 있는지 궁금해 했습니다.",
    "그 중에서 민준이라는 호기심 많은 소년이 숲의 비밀을 밝혀내고 싶었습니다."
]

prompts = [
    "Once upon a time, there was a mystical forest located on the edge of a small village.",
    "This forest was filled with the sounds of birds singing and trees dancing.",
    "However, the villagers thought the forest was too deep and maze-like, so no one dared to venture deep inside.",
    "The children always wondered what secrets the forest held.",
    "Among them, a curious boy named Minjun wanted to uncover the secrets of the forest."
]
