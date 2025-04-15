import os
from dotenv import load_dotenv
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.gpt_generator import generate_article
from utils.wordpress_client import publish_to_wordpress
from utils.telegram_notify import send_telegram_message

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
    date = row.get("Дата публикации")
    title = row.get("Тема")
    keywords = row.get("Ключевые слова")
    status = row.get("Статус", "").lower()
    comment = row.get("Комментарии", "")
    category_name = row.get("Рубрика", "Технологии")
    category_id = category_map.get(category_name, 1)
    
    if date <= today and status == "к публикации":
        print(f"\n🔄 Обработка темы: {title}")
        try:
            print("🧠 Генерация статьи...")
            content = generate_article(title, keywords)
            print("✅ Генерация завершена.")

            print("📤 Публикация в WordPress...")
            link = publish_to_wordpress(title, content, category_id)
            print(f"✅ Пост опубликован: {link}")

            message = f"✅ Статья опубликована: <b>{title}</b>\n🔗 {link}\n📝 {comment}"
            send_telegram_message(message)
            print("📩 Уведомление отправлено в Telegram.")

            sheet.update_cell(i + 2, 4, "опубликовано")
            print("📊 Статус обновлён в Google Sheets.")

        except Exception as e:
            print(f"❌ Ошибка при публикации статьи '{title}': {e}")
            try:
                send_telegram_message(f"❌ Ошибка публикации статьи '{title}': {e}")
            except Exception as telegram_error:
                print(f"⚠️ Ошибка при отправке в Telegram: {telegram_error}")
            raise
