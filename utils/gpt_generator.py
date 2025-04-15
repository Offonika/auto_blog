# utils/gpt_generator.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# === Загрузка переменных окружения ===
load_dotenv()

# === Установка переменных прокси ===
proxy_url = "http://user150107:dx4a5m@185.176.95.125:8509"
os.environ["HTTP_PROXY"] = proxy_url
os.environ["HTTPS_PROXY"] = proxy_url

# === Инициализация OpenAI клиента ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_article(title: str, keywords: str, system_prompt=None, role=None, temperature=0.7) -> str:
    messages = [
        {"role": "system", "content": system_prompt or "Ты опытный копирайтер для блога технологичного бренда."},
        {"role": "user", "content": f"Напиши SEO-оптимизированную статью на тему '{title}'. Ключевые слова: {keywords}. Введение, 2-3 смысловых блока, заключение. Стиль: информационный, доступный, техничный."}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        max_tokens=1500,
    )

    return response.choices[0].message.content.strip()
