import json
import os
import re
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

load_dotenv()

RECIPES_FILE = os.path.join("data", "recipes.json")

_STOPWORDS = {
    "и", "в", "с", "на", "из", "для", "по", "или", "без",
    "не", "до", "от", "за", "под", "как", "что", "это",
    "блюдо", "блюда", "рецепт", "рецепты", "приготовить",
    "хочу", "хочется", "можно", "сделать",
}

def load_recipes() -> list[dict]:
    with open(RECIPES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_recipe_by_id(recipe_id: int) -> dict | None:
    for r in load_recipes():
        if r.get("id") == recipe_id:
            return r
    return None

def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[а-яёa-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 1]

def _recipe_to_document(recipe: dict) -> list[str]:
    parts = (
        (recipe.get("name", "") + " ") * 3
        + (" ".join(recipe.get("tags", [])) + " ") * 2
        + " ".join(recipe.get("ingredients", []))
    )
    return _tokenize(parts)

def _filter_by_restrictions(recipes: list[dict], restrictions: str) -> list[dict]:
    restr_lower = restrictions.lower()
    result = [
        r for r in recipes
        if not any(
            kw in restr_lower
            for kw in [f.lower() for f in r.get("restrictions_forbidden", [])]
        )
    ]
    return result or recipes

_RELEVANCE_THRESHOLD = 0.3
def _bm25_candidates(
    recipes: list[dict],
    query: str,
    top_n: int = 3,
) -> list[dict]:

    corpus = [_recipe_to_document(r) for r in recipes]
    bm25 = BM25Okapi(corpus)

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scores = bm25.get_scores(query_tokens)

    normalized = [s / len(query_tokens) for s in scores]

    best_score = max(normalized)
    if best_score < _RELEVANCE_THRESHOLD:
        return []

    ranked = sorted(range(len(normalized)), key=lambda i: normalized[i], reverse=True)
    top = [i for i in ranked if normalized[i] >= _RELEVANCE_THRESHOLD][:top_n]

    return [recipes[i] for i in top]

def find_recipe_candidates(
    user_query: str,
    user_profile: dict,
    top_n: int = 3,
) -> list[dict]:
    recipes = load_recipes()
    if not recipes:
        return []

    restrictions = user_profile.get("restrictions", "нет")
    compatible = _filter_by_restrictions(recipes, restrictions)
    return _bm25_candidates(compatible, user_query, top_n=top_n)