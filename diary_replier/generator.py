import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from openai import APIError, RateLimitError

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

SYSTEM_BASE = (
    "너는 한국어로 답하는 '일기 답장 비서'야. 공감 먼저, 해결책은 최대 2개."
    "가르치려 들지 말고, 판단/진단/낙인 금지. 사적 정보 요구 금지."
    "반말을 쓰되 존중 유지. 과장 없이 현실적인 톤."
)
EXAMPLES = [
    {
        "text": "요즘 너무 피곤해서 뭐든 시작이 힘들어.",
        "reply_short": "요즘 많이 지쳤구나. 잠깐 쉬어가도 괜찮아.",
        "reply_normal": "피곤이 쌓이면 의욕이 떨어지는 게 당연해. 오늘은 욕심내지 말고 작은 목표 하나만 정하고, 쉬는 시간도 계획에 넣어보자."
    },
    {
        "text": "친구랑 다투고 나니 마음이 복잡해.",
        "reply_short": "속상했겠다. 네 마음을 솔직히 전해보는 것도 도움이 돼.",
        "reply_normal": "다툼 뒤엔 마음이 흔들리기 마련이야. 감정이 가라앉은 뒤에, 네가 느낀 핵심을 부드럽게 전해보자. 관계는 대화로 단단해져."
    }
]

def _examples_block() -> str:
    lines = ["[예시] 아래 형식을 참고해 답변 톤과 길이를 맞춰라."]
    for ex in EXAMPLES:
        lines.append(f"- (일기) {ex['text']}")
        lines.append(f"  (짧은답) {ex['reply_short']}")
        lines.append(f"  (보통답) {ex['reply_normal']}")
    return "\n".join(lines)

def _build_prompt_json(text: str, mood: str | None, preset: str) -> str:
    style = PRESETS.get(preset, PRESETS["warm"])
    mood_line = mood or "미지정"
    return f"""
{_examples_block()}

[일기]
{text}

[지침]
- 말투 preset: {preset} ({"/".join(PRESETS.keys())})
- 기분 힌트: {mood_line}
- 스타일: {style}
- 구조: 요점 1줄 → 공감 1줄 → 제안 1~2개(선택)
- reply_short: 두세 문장(100자 내외), reply_normal: 200~280자

반드시 아래 JSON으로만 답해. 그 외 문자는 출력하지 마.
{{"reply_short":"...", "reply_normal":"..."}}
""".strip()

PRESETS = {
    "warm": "따뜻하고 다정하게. 위로 + 구체적 제안 1~2개.",
    "coach": "직설적이되 예의 있게. TODO 2~3개를 번호로.",
    "short": "핵심만 두세 문장.",
}

def _call_with_retry(fn, max_retry: int = 3, base_wait: float = 0.8):
    """
    OpenAI 호출 재시도(429/5xx 대응). 지수 백오프.
    """
    for i in range(max_retry):
        try:
            return fn()
        except (RateLimitError, APIError) as e:
            if i == max_retry - 1:
                raise
            time.sleep(base_wait * (2 ** i))

def _build_prompt_json(text: str, mood: str | None, preset: str) -> str:
    style = PRESETS.get(preset, PRESETS["warm"])
    mood_line = mood or "미지정"
    # 모델이 반드시 JSON만 출력하도록 강제
    return f"""
[일기]
{text}

[지침]
- 말투 preset: {preset} ({"/".join(PRESETS.keys())})
- 기분 힌트: {mood_line}
- 스타일: {style}
- 구조: 요점 1줄 → 공감 1줄 → 제안 1~2개(선택)
- reply_short: 두세 문장(100자 내외), reply_normal: 200~280자

반드시 아래 JSON으로만 답해. 그 외 문자는 출력하지 마.
{{"reply_short":"...", "reply_normal":"..."}}
""".strip()

def generate_pair(text: str, mood: str | None, preset: str) -> tuple[str, str]:
    """
    단일 호출로 reply_short / reply_normal 동시 생성 (JSON 파싱).
    """
    prompt = _build_prompt_json(text, mood, preset)
    res = _call_with_retry(lambda: _client.responses.create(
        model=_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_BASE},
            {"role": "user", "content": prompt},
        ],
    ))
    # JSON 파싱
    try:
        data = json.loads(res.output_text)
        rs = (data.get("reply_short", "") or "").strip()
        rn = (data.get("reply_normal", "") or "").strip()
        if not rs or not rn:
            raise ValueError("empty fields")
        return rs, rn
    except Exception:
        # 파싱 실패 시 최소한의 폴백 (둘 다 한 본문으로 반환)
        txt = res.output_text.strip()
        return txt[:120], txt
