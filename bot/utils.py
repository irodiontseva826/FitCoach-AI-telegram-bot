import os
from google import genai
from dotenv import load_dotenv
from bot.config import GEMINI_MODEL
load_dotenv()

client = genai.Client(api_key=os.getenv("LLM_API_KEY"))

async def ask_llm(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "⚠️ Сервер перегружен или лимит запросов исчерпан. Попробуй через минуту 🙏"