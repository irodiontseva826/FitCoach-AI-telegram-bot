import os
from google import genai
from dotenv import load_dotenv
from bot.config import GEMINI_MODEL
from aiogram.types import Message

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


async def send_plan_split(message: Message, plan: str):
    split_marker = "ПРОГРАММА ТРЕНИРОВОК"
    idx = plan.find(split_marker)
    chunk_size = 4000

    if idx != -1:
        nutrition = plan[:idx].strip()
        workout = plan[idx:].strip()

        await message.answer("🥗 *ПЛАН ПИТАНИЯ НА 7 ДНЕЙ:*", parse_mode="Markdown")
        for i in range(0, len(nutrition), chunk_size):
            await message.answer(nutrition[i:i + chunk_size])

        await message.answer("💪 *ПЛАН ТРЕНИРОВОК:*", parse_mode="Markdown")
        for i in range(0, len(workout), chunk_size):
            await message.answer(workout[i:i + chunk_size])
    else:
        for i in range(0, len(plan), chunk_size):
            await message.answer(plan[i:i + chunk_size])