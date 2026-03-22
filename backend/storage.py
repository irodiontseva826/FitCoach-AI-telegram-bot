import json
import os
from datetime import datetime
 
PLANS_DIR = "data/plans"
 
 
def _get_user_file(user_id: int) -> str:
    os.makedirs(PLANS_DIR, exist_ok=True)
    return os.path.join(PLANS_DIR, f"{user_id}.json")
 
 
def save_plan(user_id: int, profile: dict, plan_text: str) -> None:
    """Сохраняет профиль и сгенерированный план в JSON-файл пользователя."""
    payload = {
        "user_id": user_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "profile": profile,
        "plan": plan_text,
    }
    with open(_get_user_file(user_id), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
 
 
def load_plan(user_id: int) -> dict | None:
    """Загружает последний сохранённый план пользователя. Возвращает None если файла нет."""
    path = _get_user_file(user_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)