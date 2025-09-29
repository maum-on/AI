class BaseLLMClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """모든 LLM 클라이언트는 이 인터페이스를 따라야 함"""
        raise NotImplementedError
