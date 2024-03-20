import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일에서 환경 변수를 불러오는 부분입니다.
load_dotenv()

# Stability AI 서버 정보와 API 키를 환경 변수에서 설정합니다.
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
STABILITY_KEY = os.environ.get("STABILITY_KEY")
DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY")
FIREBASE_SERVER_KEY = os.environ.get("FIREBASE_SERVER_KEY")


# 경로 설정 및 필요한 디렉터리 생성
base_dir = Path(__file__).resolve().parent/"static"
image_path = str(base_dir/"images")
image_font_path = str(base_dir / "font" / "SpoqaHanSansNeo-Bold.ttf")
audio_path = str(base_dir / "audios")
video_path = str(base_dir / "videos")