import requests


class OllamaClient:
    def __init__(self, base_url: str, model: str, temperature: float = 0.1):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "").strip()