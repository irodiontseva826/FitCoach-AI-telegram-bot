import os
from google import genai
from dotenv import load_dotenv
from bot.config import GEMINI_MODEL
from backend.storage import save_plan, load_plan
from bot.prompts import ADJUST_PROMPT_TEMPLATE

load_dotenv()

proxy = os.getenv("SOCKS5_PROXY")
if proxy:
    os.environ["HTTPS_PROXY"] = proxy
    os.environ["HTTP_PROXY"] = proxy

client = genai.Client(api_key=os.getenv("LLM_API_KEY"))

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

async def adjust_plan(user_id: int, user_input: str) -> str:
    try:
        record = load_plan(user_id)

        if not record:
            return "❗ Сначала создай план с помощью кнопки «Создать новый план»"

        profile = record.get("profile", {})
        last_plan = record.get("plan", "")

        profile_text = "\n".join([f"{k}: {v}" for k, v in profile.items()])

        prompt = ADJUST_PROMPT_TEMPLATE.format(
            profile_text=profile_text,
            last_plan=last_plan,
            user_input=user_input
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        new_plan = response.text

        if not new_plan:
            return "⚠️ Не удалось сгенерировать план. Попробуй ещё раз."

        save_plan(user_id, profile, new_plan)

        return {"ok": True, "data": new_plan}

    except Exception as e:
        print(f"ADJUST ERROR: {e}")
        return {"ok": False, "data": "⚠️ Сервер перегружен или лимит запросов исчерпан. Попробуй через минуту 🙏"}