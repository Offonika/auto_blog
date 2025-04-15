# utils/gpt_generator.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# === Загрузка переменных окружения ===
load_dotenv()

# === Настройка прокси ===
proxy_url = "http://user150107:dx4a5m@185.176.95.125:8509"
os.environ["HTTP_PROXY"] = proxy_url
os.environ["HTTPS_PROXY"] = proxy_url

# === Инициализация OpenAI клиента ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_article(title: str, keywords: str, system_prompt=None, role=None, temperature=0.7, focus_keyword=None) -> str:
    focus = focus_keyword or keywords.split(",")[0].strip()

    # Обновляем заголовок, если фокусный ключевик не включён
    if focus.lower() not in title.lower():
        title += f": {focus.capitalize()}"

    messages = [
        {
            "role": "system",
            "content": system_prompt or (
                "Ты SEO-копирайтер, создающий статьи для технологичного блога Offonika. "
                "Пиши в информационно-полезном, но структурированном стиле. Не менее 600 слов. "
                "Используй фокусный ключевик в заголовке, первом абзаце, теле статьи и заключении. "
                "Повтори его минимум 3–4 раза, чтобы соответствовать требованиям Rank Math SEO."
            )
        },
        {
            "role": "user",
            "content": (
                f"Напиши SEO-оптимизированную статью на тему: '{title}'.\n"
                f"Фокусный ключевик: {focus}.\n"
                f"Начни статью с абзаца, в котором ключевик входит в первое предложение.\n"
                f"Структура: краткое вступление, 2–3 смысловых блока, заключение. Не менее 600 слов.\n"
                f"Добавь блок в начале:\n"
                f"**Slug**: {focus.replace(' ', '-').lower()}\n"
                f"**Краткое описание**: {focus.capitalize()} — важная тема. Узнай, как она влияет на технологии."
            )
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        max_tokens=2000
    )

    return response.choices[0].message.content.strip()
