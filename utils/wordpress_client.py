# utils/wordpress_client.py

import os
import re
import requests
from dotenv import load_dotenv
from utils.auth import get_jwt_token
from utils.image_generator import generate_image, upload_to_wordpress

load_dotenv()

def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_]+", "-", text)

def publish_to_wordpress(title, content, category_id=1, focus_keyword=""):
    token = get_jwt_token()
    url = os.getenv("WP_URL") + "/wp-json/wp/v2/posts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    slug = slugify(focus_keyword or title)
    excerpt = f"Краткое описание: {focus_keyword}. Узнайте больше в статье!"

    # Попробуем сгенерировать обложку
    try:
        prompt = f"Обложка к статье на тему: {focus_keyword}, в технологичном и минималистичном стиле"
        image_url = generate_image(prompt)
        media_id = upload_to_wordpress(image_url)
    except Exception as e:
        print(f"⚠️ Ошибка генерации/загрузки обложки: {e}")
        media_id = None

    data = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "slug": slug,
        "status": "publish",
        "format": "standard",
        "categories": [category_id],
        "featured_media": media_id or 0
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()["link"]
