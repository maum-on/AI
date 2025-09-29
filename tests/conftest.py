# tests/conftest.py
import os
import pytest

# 세션 시작 시 가짜 키 (혹시 모를 import 대비)
@pytest.fixture(autouse=True, scope="session")
def fake_api_key():
    os.environ["OPENAI_API_KEY"] = "test-dummy-key"

# 공통 텍스트
@pytest.fixture
def sample_text():
    return "오늘은 프레젠테이션이 끝나서 뿌듯했지만, 조금 피곤했어."

@pytest.fixture
def crisis_text():
    return "요즘 너무 힘들어서 다 끝내버리고 싶다는 생각이 들어."

# 더미 LLM
class DummyLLMClient:
    def call(self, *args, **kwargs):
        # analyzer일 때 JSON, generator일 때 텍스트—간단하게 분기
        sys = args[0] if args else ""
        if "분석" in sys or "JSON" in sys or "도우미" in sys:
            return (
                '{"valence":"neutral","emotions":["피곤","성취"],'
                '"keywords":["프레젠테이션","피곤"],'
                '"summary":"발표를 마치고 성취감과 피곤함을 느낌"}'
            )
        return "오늘 하루 고생 많으셨어요. 발표 마무리하며 성취감도 크셨겠죠!"

@pytest.fixture(autouse=True)
def patch_get_llm(monkeypatch):
    # analyzer/generator의 get_llm을 더미로 교체
    monkeypatch.setattr("diary_replier.analyzer.get_llm", lambda: DummyLLMClient(), raising=True)
    monkeypatch.setattr("diary_replier.generator.get_llm", lambda: DummyLLMClient(), raising=True)
