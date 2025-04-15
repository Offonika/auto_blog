# utils/image_generator.py

import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from utils.auth import get_jwt_token

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(prompt: str) -> str:
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

def upload_to_wordpress(image_url: str) -> int:
    image_data = requests.get(image_url).content
    filename = "cover.jpg"

    url = os.getenv("WP_URL") + "/wp-json/wp/v2/media"
    headers = {
        "Authorization": f"Bearer {get_jwt_token()}",
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/jpeg"
    }

    response = requests.post(url, headers=headers, data=image_data)
    if response.status_code != 201:
        raise Exception("❌ Ошибка загрузки изображения в WordPress: " + response.text)
    
    return response.json()["id"]
