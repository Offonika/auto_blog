# utils/prompt_builder.py

def build_cover_prompt(title: str, focus_keyword: str = "", category: str = "", system_prompt: str = "", keywords: str = "", role: str = "", temperature: float = 0.7) -> str:
    """
    Формирует промт для генерации обложки статьи с учётом смысла, категории и подсказок из текстового промта и ключевых слов.
    """
    semantic_subject = focus_keyword or title
    category_text = category.strip() or "технологии"
    instruction_text = system_prompt.strip() or ""

    prompt_data = {
        "Тема": f"обложка для статьи в рубрике '{category_text}'",
        "Ключевые слова": f"подсказки из ключевых слов: {keywords.strip()}",
        "Системные инструкции (промт)": instruction_text,
        "Роль": role,
        "Температура": f"{temperature}",
        "формат": "квадратное изображение, 1024x1024, без текста, готово для блога"
    }
    return ", ".join(prompt_data.values())