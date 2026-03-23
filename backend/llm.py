import os
from google import genai
from dotenv import load_dotenv
from bot.config import GEMINI_MODEL
from backend.storage import save_plan

load_dotenv()
os.environ["GEMINI_API_KEY"] = str(os.getenv('LLM_API_KEY'))

client = genai.Client()

def build_prompt(data: dict) -> str:
    return (
        f"Я {data['gender']}, мне {data['age']} лет. "
        f"Рост {data['height']} см, вес {data['weight']} кг. "
        f"Цель: {data['goal']}. "
        f"Уровень подготовки: {data['level']}. "
        f"Готов(а) тренироваться {data['training_days']} дней в неделю. "
        f"Место тренировок: {data['equipment']}. "
        f"Ограничения в питании: {data['restrictions']}. "
        "Составь подробный план питания и тренировок на неделю. "
        "Важно, чтобы прорабатывались разные группы мышц, "
        "а питание было разнообразным и доступным в средней полосе России."
    )

async def generate_plan(user_id: int, data: dict) -> str:
    prompt = build_prompt(data)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    plan = response.text
    save_plan(user_id, data, plan)
    return plan