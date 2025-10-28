# diary_replier/llm_providers/openai_client.py
from typing import Optional, List, Dict, Any  # ✅ 추가
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class OpenAILLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("DIARY_MODEL_NAME", "gpt-4o-mini")
        self._client = OpenAI(api_key=self.api_key) if OpenAI else None

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.6) -> str:
        # openai 패키지 없거나 키 없으면 폴백
        if not self._client:
            # 테스트/로컬용 폴백 문자열
            return "LLM fallback: openai 패키지 없음 또는 API 키 미설정"
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
