import os
import deepl
from dotenv import load_dotenv


# DeepL_api 클래스는 DeepL 번역 API를 사용하기 위한 래퍼(wrapper) 클래스입니다.
class Deepl_api:
    # 생성자에서 API 키를 인자로 받고, 이를 검증한 후 deepl.Translator 객체를 초기화합니다.
    def __init__(self, api_key=None):
        if api_key is None:
            raise ValueError("API 키를 제공해야 합니다.")  # API 키가 제공되지 않으면 오류를 발생시킵니다.
        self.translator = deepl.Translator(api_key)

    # translate_text 메서드는 주어진 텍스트(들)를 대상 언어로 번역합니다.
    def translate_text(self, text, target_lang="FR"):
        try:
            # translate_text 메서드를 사용하여 번역을 시도합니다.
            result = self.translator.translate_text(text, target_lang=target_lang)
            return result  # 번역 결과를 반환합니다.
        except deepl.DeepLException as e:
            print(f"DeepL API 오류: {e}")  # DeepL API에서 오류가 발생하면 콘솔에 출력합니다.
            return None


# 스크립트가 직접 실행될 때만 아래의 코드가 실행됩니다.
if __name__ == "__main__":
    load_dotenv()  # .env 파일로부터 환경 변수를 로드합니다.
    auth_key = os.getenv("DEEPL_API_KEY")  # DEEPL_API_KEY 환경 변수를 가져옵니다.

    if not auth_key:
        raise ValueError("DEEPL_API_KEY가 설정되지 않았습니다. 환경 변수를 확인하세요.")  # API 키가 없으면 오류를 발생시킵니다.

    deepl_api = Deepl_api(api_key=auth_key)  # Deepl_api 객체를 초기화합니다.

    # 번역을 수행합니다. 일본어와 스페인어 문장을 영국 영어로 번역합니다.
    translated_kor = deepl_api.translate_text(
        ["お元気ですか？", "¿Cómo estás?", "Apa kabare?"], target_lang="KO"
    )
    translated_eng = deepl_api.translate_text(
        ["お元気ですか？", "¿Cómo estás?", "Apa kabare?"], target_lang="EN-US"
    )

    # 번역된 결과와 감지된 원본 언어를 출력합니다.
    print(f"[0]번 index Korean : {translated_kor[0].text}")  # 첫 번째 문장의 번역 결과를 출력합니다.
    print(f" 언어 : {translated_kor[0].detected_source_lang}")  # 첫 번째 문장의 원본 언어 코드를 출력합니다. ("JA"는 일본어를 의미합니다.)
    print(f"[0]번 index English : {translated_eng[0].text}")  # 첫 번째 문장의 번역 결과를 출력합니다.
    print(f" 언어 : {translated_eng[0].detected_source_lang}")  # 첫 번째 문장의 원본 언어 코드를 출력합니다. ("JA"는 일본어를 의미합니다.)

    # print(f"멀티로 번역시 index별로 출력 해야함 : {translated_text}")  # 전체 번역 결과 리스트를 출력합니다.
