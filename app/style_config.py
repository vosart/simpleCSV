# ------------------------
# Основные стили
# ------------------------
STYLE_CONFIG = {
    # Заголовок
    "header": {
        "font": {"bold": True, "color": "FFFFFF"},
        "fill": "4F81BD",
        "alignment": "center"
    },
    # Положительные суммы
    "money_positive": {
        "font": {"bold": False, "color": "006100"},
        "fill": "C6EFCE",
        "alignment": "right"
    },
    # Отрицательные суммы
    "money_negative": {
        "font": {"bold": False, "color": "9C0006"},
        "fill": "FFC7CE",
        "alignment": "right"
    },
    # Текст
    "text": {
        "font": {"bold": False, "color": "000000"},
        "alignment": "left"
    },
    # Дата
    "date": {
        "font": {"bold": False, "color": "000000"},
        "alignment": "center"
    },
    # Conditional rules
    "rules": [
        {
            # Красное выделение, если расход больше 100_000
            "condition": "value < -100000",
            "style": {
                "font": {"bold": True, "color": "FFFFFF"},
                "fill": "FF0000",
                "alignment": "right"
            }
        },
        {
            # Зелёное выделение, если доход больше 500_000
            "condition": "value > 500000",
            "style": {
                "font": {"bold": True, "color": "FFFFFF"},
                "fill": "008000",
                "alignment": "right"
            }
        }
    ]
}

# ------------------------
# Подсказки для column-aware detection
# ------------------------
COLUMN_HINTS = {
    "сумма": "money",
    "дата": "date",
    "категория": "text",
    "описание": "text",
    "контрагент": "text"
}