import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()  # Обязательно для загрузки переменных, если используется отдельно

def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_]+", "-", text)

def get_jwt_token():
    print("🔐 Получение JWT-токена...")
    url = os.getenv("WP_URL") + "/wp-json/jwt-auth/v1/token"
    response = requests.post(url, json={
        "username": os.getenv("WP_USERNAME"),
        "password": os.getenv("WP_PASSWORD")
    })

    if response.status_code != 200:
        print("❌ Ошибка авторизации WordPress:", response.status_code)
        print(response.text)
        raise Exception("Не удалось получить JWT токен")

    token = response.json()["token"]
    print("✅ JWT-токен получен.")
    return token

def publish_to_wordpress(title, content, category_id=1):
    token = get_jwt_token()
    url = os.getenv("WP_URL") + "/wp-json/wp/v2/posts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    slug = slugify(title)
    excerpt = content.strip().split("\n")[0][:150]

    data = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "slug": slug,
        "status": "publish",
        "format": "standard",
        "categories": [category_id]
    }

    print(f"➡️ Данные для отправки в WordPress:\n{data}")

    response = requests.post(url, json=data, headers=headers)

    print(f"📬 Ответ от WordPress: {response.status_code}")
    if response.status_code != 201:
        print("❌ Ошибка при публикации:")
        print(response.text)

    response.raise_for_status()
    return response.json()["link"]
