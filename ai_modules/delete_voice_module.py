import requests
import httpx

class Delete_voice_module:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"xi-api-key": api_key}
        self.url = "https://api.elevenlabs.io/v1/voices/"

    async def delete_voice(self, voice_id: str):
        print("---- [delete_voice] ----")

        # response = requests.request("DELETE", self.url + voice_id, headers=self.headers)
        # print(response.text)

        async with httpx.AsyncClient() as client:
            response = await client.delete(self.url + voice_id, headers=self.headers)
        print(response.text)
        return response

