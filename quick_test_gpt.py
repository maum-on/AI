import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

res = client.responses.create(
    model="gpt-4o-mini",
    input="테스트: 지금 GPT 응답 잘 오니?"
)
print(res.output_text)