# auto_post_blog.py

import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from utils.gpt_generator import generate_article
from utils.wordpress_client import publish_to_wordpress
from utils.telegram_notify import send_telegram_message
from utils.image_generator import generate_image
from utils.prompt_builder import build_cover_prompt

# === Логирование ===
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "auto_post.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# === Загрузка .env ===
load_dotenv()

# === Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"), scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet(os.getenv("GOOGLE_SHEET_TAB_NAME"))

# === Карта рубрик ===
category_map = {
    "Технологии": 1,
    "Советы": 2,
    "Обзоры": 3,
    "Маркетинг": 14,
    "Соцсети": 15,
    "E-commerce": 16,
    "Бизнес": 17,
    "Медиа": 18,
    "Цифровая безопасность": 19
}

# === Чтение таблицы ===
rows = sheet.get_all_records()
today = datetime.now().strftime("%Y-%m-%d")

for i, row in enumerate(rows):
    raw_date = row.get("Дата публикации")

    # Обработка даты
    if isinstance(raw_date, int):
        base_date = datetime(1899, 12, 30)
        date = (base_date + timedelta(days=raw_date)).strftime("%Y-%m-%d")
    elif isinstance(raw_date, str):
        try:
            date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            try:
                date = datetime.strptime(raw_date, "%d.%m.%Y").strftime("%Y-%m-%d")
            except ValueError:
                logging.warning(f"⚠️ Некорректная дата: {raw_date}")
                continue
    else:
        continue

    title = row.get("Тема")
    keywords = row.get("Ключевые слова")
    status = row.get("Статус", "").lower()
    comment = row.get("Комментарии", "")
    category_name = row.get("Рубрика", "Технологии")
    system_prompt = row.get("Системные инструкции (промт)", "")
    role = row.get("Роль", "")
    temperature = float(row.get("Температура", 0.7) or 0.7)
    focus_keyword = row.get("Фокусный ключевик", "")

    # Новые визуальные поля
    style = row.get("Стиль", "")
    composition = row.get("Композиция", "")
    color_palette = row.get("Цветовая палитра", "")
    details = row.get("Детализация", "")

    # Категории
    category_names = [name.strip() for name in category_name.split(",")]
    category_ids = [category_map.get(name, 1) for name in category_names if name in category_map]
    if not category_ids:
        category_ids = [1]

    if date <= today and status == "к публикации":

        if focus_keyword and focus_keyword.lower() not in title.lower():
            title += f": {focus_keyword.capitalize()}"

        print(f"\n🔄 Обработка темы: {title}")
        logging.info(f"🔄 Обработка темы: {title}")

        try:
            print("🧠 Генерация статьи...")
            content = generate_article(title, keywords, system_prompt, role, temperature, focus_keyword)
            print("✅ Генерация завершена.")
            logging.info("✅ Генерация завершена.")

            print("🧠 Генерация промта обложки...")
            cover_prompt = build_cover_prompt(
                title=title,
                focus_keyword=focus_keyword,
                category=category_name,
                system_prompt=system_prompt,
                keywords=keywords,
                role=role,
                temperature=temperature,
                style=style,
                composition=composition,
                color_palette=color_palette,
                details=details
            )
            print(f"🖼 Промт генерации изображения (dalle): {cover_prompt}")

            try:
                image_url = generate_image(cover_prompt)
                logging.info(f"🖼 Изображение сгенерировано: {image_url}")
            except Exception as img_error:
                print(f"⚠️ Ошибка генерации обложки: {img_error}")
                logging.warning(f"⚠️ Ошибка генерации обложки: {img_error}")
                image_url = ""

            print("📤 Публикация в WordPress...")
            link = publish_to_wordpress(title, content, category_ids, focus_keyword, image_url)
            print(f"✅ Пост опубликован: {link}")
            logging.info(f"✅ Пост опубликован: {link}")

            message = f"✅ Статья опубликована: <b>{title}</b>\n🔗 {link}\n📝 {comment}"
            send_telegram_message(message)
            print("📩 Уведомление отправлено в Telegram.")
            logging.info("📩 Уведомление отправлено в Telegram.")

            sheet.update_cell(i + 2, 4, "опубликовано")
            sheet.update_cell(i + 2, 8, link)
            print("📊 Статус и ссылка обновлены в Google Sheets.")
            logging.info("📊 Статус и ссылка обновлены в Google Sheets.")

        except Exception as e:
            print(f"❌ Ошибка при публикации статьи '{title}': {e}")
            logging.error(f"❌ Ошибка при публикации статьи '{title}': {e}")
            try:
                send_telegram_message(f"❌ Ошибка публикации: {title}\n{e}")
            except Exception as telegram_error:
                print(f"⚠️ Ошибка отправки в Telegram: {telegram_error}")
                logging.warning(f"⚠️ Ошибка отправки в Telegram: {telegram_error}")
