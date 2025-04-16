# utils/prompt_builder.py

def build_cover_prompt(
    title: str,
    focus_keyword: str = "",
    category: str = "",
    system_prompt: str = "",
    keywords: str = "",
    role: str = "",
    temperature: float = 0.7,
    style: str = "",
    composition: str = "",
    color_palette: str = "",
    details: str = ""
) -> str:
    """
    Генерирует промт для изображения в формате "Ключ: Значение",
    где ключи соответствуют колонкам Google Sheets.
    """
    prompt_data = {
        "Тема": title.strip(),
        "Рубрика": category.strip() or "технологии",
        "Ключевые слова": keywords.strip(),
        "Системные инструкции (промт)": system_prompt.strip(),
        "Роль": role.strip(),
        "Температура": str(temperature),
        "Стиль": style.strip(),
        "Композиция": composition.strip(),
        "Цветовая палитра": color_palette.strip(),
        "Детализация": details.strip(),
        "Формат": "квадратное изображение, 1024x1024, без текста, готово для блога"
    }

    return ", ".join([f"{k}: {v}" for k, v in prompt_data.items() if v])
