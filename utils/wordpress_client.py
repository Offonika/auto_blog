import os
import requests
import re
from utils.image_generator import upload_to_wordpress
from utils.auth import get_jwt_token


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_]+", "-", text)


# === Обновлённая карта рубрик ===
category_map = {
    "Советы": 4,
    "Технологии": 2,
    "Маркетинг": 14,
    "Соцсети": 15,
    "E-commerce": 16,
    "Бизнес": 17,
    "Медиа": 18,
    "Цифровая безопасность": 19,
    "Обзоры": 3
}


def publish_to_wordpress(title, content, category_ids=None, focus_keyword="", image_url=None):
    token = get_jwt_token()
    url = os.getenv("WP_URL") + "/wp-json/wp/v2/posts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # === Генерация слага на основе ключевика ===
    slug = slugify(focus_keyword or title)
    excerpt = f"{focus_keyword.capitalize()}. Узнайте больше в статье."

    # === Загрузка обложки, если передана ===
    media_id = 0
    if image_url:
        try:
            media_id = upload_to_wordpress(image_url)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки обложки: {e}")
            media_id = 0

    # === Обработка рубрик ===
    if not category_ids:
        category_ids = [1]  # Fallback: без рубрики

    # === Публикация ===
    data = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "slug": slug,
        "status": "publish",
        "format": "standard",
        "categories": category_ids,
        "featured_media": media_id,
        "meta": {
            "rank_math_focus_keyword": focus_keyword
        }
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()

    post = response.json()

    # === Читаемый URL: blog.site.ru/slug
    readable_link = f"{os.getenv('WP_URL')}/{slug}/"
    return readable_link or post.get("link")
