import os
import openai
from dotenv import load_dotenv

# === Загрузка переменных окружения ===
load_dotenv()

# === Установка ключа OpenAI ===
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Настройка прокси (если задан) ===
proxy_url = "http://user150107:dx4a5m@185.176.95.125:8509"
openai.proxy = {
    "http": proxy_url,
    "https": proxy_url
}

def generate_article(title: str, keywords: str) -> str:
    messages = [
        {"role": "system", "content": "Ты опытный копирайтер для блога технологичного бренда."},
        {"role": "user", "content": f"Напиши SEO-оптимизированную статью на тему '{title}'. Ключевые слова: {keywords}. Введение, 2-3 смысловых блока, заключение. Стиль: информационный, доступный, техничный."}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message["content"].strip()
