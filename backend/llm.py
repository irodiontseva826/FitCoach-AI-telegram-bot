import os
from google import genai
from dotenv import load_dotenv
from bot.config import GEMINI_MODEL

load_dotenv()
os.environ["GEMINI_API_KEY"]=str(os.getenv('LLM_API_KEY'))

client = genai.Client()

response = client.models.generate_content(
    model=GEMINI_MODEL, contents="Привет. Я женщина, мне 22 года, у меня достаточно хорошая фигура и периодически в жизни присутсвует физическая активность. Мой рост 166, вес 48. Я хочу набрать мышечную массу. Готова ходить в зал 2 раза в неделю. Составь мне план питания и тренировок на неделю. Важно, чтобы прорабатывались различные группы мышщ,  а питание было разнообразным и доступным в плане продуктов в средней полосе России."
)
print(response.text)