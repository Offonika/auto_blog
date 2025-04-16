# Файл: utils/image_generator.py

import os
import requests
import base64
import mimetypes
import re
from io import BytesIO
from openai import OpenAI
from unidecode import unidecode
from utils.auth import get_jwt_token  # 🔑 Для получения токена
from utils.prompt_builder import build_cover_prompt  # Новый импорт

# === Инициализация OpenAI (DALL·E) ===
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(prompt: str, model: str = None) -> str:
    """
    Универсальный обработчик генерации изображений
    """
    model = model or os.getenv("IMAGE_GEN_MODEL", "dalle")
    print(f"🖼 Промт генерации изображения ({model}): {prompt}")

    if model == "dalle":
        return generate_dalle(prompt)
    elif model == "leonardo":
        return generate_leonardo(prompt)
    elif model == "stable_diffusion":
        return generate_sd(prompt)
    else:
        raise ValueError(f"Неизвестная модель генерации изображений: {model}")


# === DALL·E (OpenAI) ===
def generate_dalle(prompt: str) -> str:
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    return response.data[0].url


# === Leonardo AI (пример интеграции, нужен свой API) ===
def generate_leonardo(prompt: str) -> str:
    leonardo_api_key = os.getenv("LEONARDO_API_KEY")
    url = "https://cloud.leonardo.ai/api/rest/v1/generate"

    headers = {
        "Authorization": f"Bearer {leonardo_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "modelId": os.getenv("LEONARDO_MODEL_ID", "default")
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    return data.get("generated_image_url")


# === Stable Diffusion (пример через AUTOMATIC1111 API) ===
def generate_sd(prompt: str) -> str:
    sd_url = os.getenv("SD_API_URL")  # Пример: http://127.0.0.1:7860
    payload = {
        "prompt": prompt,
        "steps": 20,
        "width": 512,
        "height": 512
    }
    response = requests.post(f"{sd_url}/sdapi/v1/txt2img", json=payload)
    result = response.json()
    image_base64 = result["images"][0]
    image_data = base64.b64decode(image_base64)

    output_path = f"generated_sd_image_{slugify(prompt[:20])}.png"
    with open(output_path, "wb") as f:
        f.write(image_data)
    return output_path


# === Загрузка изображения в WordPress ===
def upload_to_wordpress(image_url: str) -> int:
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        image_data = BytesIO(response.content)
        filename = os.path.basename(image_url.split("?")[0])
        mime_type = mimetypes.guess_type(filename)[0] or "image/jpeg"

        token = get_jwt_token()
        print(f"🔑 Токен для загрузки: {token}")

        upload_url = os.getenv("WP_URL") + "/wp-json/wp/v2/media"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        files = {
            'file': (filename, image_data, mime_type)
        }

        upload_response = requests.post(upload_url, headers=headers, files=files)
        upload_response.raise_for_status()

        media_id = upload_response.json().get("id")
        return media_id

    except Exception as e:
        print(f"❌ Ошибка загрузки изображения: {e}")
        return 0


# === Транслитерация slug ===
def slugify(text):
    text = unidecode(text)  # Преобразование кириллицы в латиницу
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_]+", "-", text)


