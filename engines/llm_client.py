import requests


class LLMClient:
    """硅基流动 SiliconFlow LLM 客户端"""

    BASE_URL = "https://api.siliconflow.cn/v1/chat/completions"

    def __init__(self, api_key, model="deepseek-ai/DeepSeek-V4-Pro"):
        self.api_key = api_key
        self.model = model

    def chat(self, system_prompt, user_prompt, max_tokens=4096, temperature=0.7):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }

        import time
        for attempt in range(3):
            try:
                resp = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=180)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except requests.exceptions.Timeout:
                if attempt < 2:
                    print(f"  [LLM] 超时，重试 {attempt+2}/3...")
                    time.sleep(5)
                else:
                    raise
            except requests.exceptions.RequestException as e:
                if attempt < 2:
                    print(f"  [LLM] 请求失败: {e}, 重试 {attempt+2}/3...")
                    time.sleep(3)
                else:
                    raise

    def __call__(self, system_prompt, user_prompt):
        return self.chat(system_prompt, user_prompt)
