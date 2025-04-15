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

# === Логирование в файл ===
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "auto_post.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# === Загрузка переменных окружения ===
load_dotenv()

# === Настройка Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"), scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet(os.getenv("GOOGLE_SHEET_TAB_NAME"))

# === Категории ===
category_map = {
    "Технологии": 1,
    "Советы": 2,
    "Обзоры": 3
}

# === Получение данных ===
rows = sheet.get_all_records()
today = datetime.now().strftime("%Y-%m-%d")

for i, row in enumerate(rows):
    raw_date = row.get("Дата публикации")
    
    # === Обработка формата даты ===
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
        logging.warning(f"⚠️ Неизвестный формат даты: {raw_date}")
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
    category_id = category_map.get(category_name, 1)

    if date <= today and status == "к публикации":

        # 🔁 Добавим фокусный ключ в заголовок, если он там не содержится
        if focus_keyword and focus_keyword.lower() not in title.lower():
            title += f": {focus_keyword.capitalize()}"

        print(f"\n🔄 Обработка темы: {title}")
        logging.info(f"🔄 Обработка темы: {title}")
        try:
            print("🧠 Генерация статьи...")
            content = generate_article(title, keywords, system_prompt, role, temperature, focus_keyword)
            print("✅ Генерация завершена.")
            logging.info("✅ Генерация завершена.")

            print("📤 Публикация в WordPress...")
            link = publish_to_wordpress(title, content, category_id, focus_keyword)
            print(f"✅ Пост опубликован: {link}")
            logging.info(f"✅ Пост опубликован: {link}")

            message = f"✅ Статья опубликована: <b>{title}</b>\n🔗 {link}\n📝 {comment}"
            send_telegram_message(message)
            print("📩 Уведомление отправлено в Telegram.")
            logging.info("📩 Уведомление отправлено в Telegram.")

            sheet.update_cell(i + 2, 4, "опубликовано")  # Статус
            sheet.update_cell(i + 2, 8, link)            # Ссылка
            print("📊 Статус и ссылка обновлены в Google Sheets.")
            logging.info("📊 Статус и ссылка обновлены в Google Sheets.")

        except Exception as e:
            print(f"❌ Ошибка при публикации статьи '{title}': {e}")
            logging.error(f"❌ Ошибка при публикации статьи '{title}': {e}")
            try:
                send_telegram_message(f"❌ Ошибка публикации статьи '{title}': {e}")
            except Exception as telegram_error:
                print(f"⚠️ Ошибка при отправке в Telegram: {telegram_error}")
                logging.warning(f"⚠️ Ошибка при отправке в Telegram: {telegram_error}")
