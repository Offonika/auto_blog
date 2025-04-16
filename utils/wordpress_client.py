import os
import requests
import re
from utils.image_generator import upload_to_wordpress
from utils.auth import get_jwt_token


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_]+", "-", text)


def publish_to_wordpress(title, content, category_id=1, focus_keyword="", image_url=""):
    token = get_jwt_token()
    url = os.getenv("WP_URL") + "/wp-json/wp/v2/posts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # === Генерация слага на основе ключевика
    slug = slugify(focus_keyword or title)
    excerpt = f"{focus_keyword.capitalize()}. Узнайте больше в статье."

    # === Загрузка обложки, если есть image_url
    media_id = None
    if image_url:
        try:
            media_id = upload_to_wordpress(image_url)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки обложки: {e}")
            media_id = None

    # === Публикация
    data = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "slug": slug,
        "status": "publish",
        "format": "standard",
        "categories": [category_id],
        "featured_media": media_id or 0,
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
