import pandas as pd
from random import choice, randint
from datetime import datetime, timedelta
import os

# Создаём папку для файлов
os.makedirs("./files", exist_ok=True)

# Генерируем даты для 300+ дней
start_date = datetime(2026, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(320)]  # 320 дней → 320 записей

# Возможные операции и контрагенты
operations = [
    "Аренда офиса",
    "Зарплата сотруднику",
    "АЗС",
    "Комиссия банка",
    "Интернет",
    "Продажа услуги",
    "Топливо",
    "Аренда оборудования",
    "Консультация",
    "Связь"
]

counteragents = [
    "ООО 'Бизнес-центр'", "Иванов И.И.", "Петров П.П.", "Сидоров С.С.",
    "Газпромнефть", "Лукойл", "Сбербанк", "Тинькофф", "Ростелеком",
    "Мегафон", "МТС", "ООО 'Техника'", "Клиент А", "Клиент Б", "Клиент В",
    "Клиент Г", "Клиент Д"
]

# Генерация данных
data = []
for i in range(len(dates)):
    op = choice(operations)
    if op == "Зарплата сотруднику":
        amount = -randint(120000, 180000)
        counteragent = choice(["Иванов И.И.", "Петров П.П.", "Сидоров С.С."])
    elif op in ["Продажа услуги", "Консультация"]:
        amount = randint(40000, 1000000)  # включаем крупные доходы
        counteragent = choice(["Клиент А", "Клиент Б", "Клиент В", "Клиент Г", "Клиент Д"])
    elif op == "Аренда офиса":
        amount = -randint(40000, 70000)
        counteragent = "ООО 'Бизнес-центр'"
    elif op == "Аренда оборудования":
        amount = -randint(25000, 55000)
        counteragent = "ООО 'Техника'"
    elif op in ["АЗС", "Топливо"]:
        amount = -randint(8000, 25000)
        counteragent = choice(["Газпромнефть", "Лукойл"])
    elif op == "Комиссия банка":
        amount = -randint(1000, 5000)
        counteragent = choice(["Сбербанк", "Тинькофф"])
    elif op in ["Интернет", "Связь"]:
        amount = -randint(1500, 3000)
        counteragent = choice(["Ростелеком", "Мегафон", "МТС"])
    else:
        amount = randint(-20000, 200000)
        counteragent = choice(counteragents)

    data.append([dates[i].strftime("%Y-%m-%d"), op, amount, counteragent])

# Создаём DataFrame
df = pd.DataFrame(data, columns=["Дата", "Описание", "Сумма", "Контрагент"])

# Сохраняем CSV
df.to_csv("./files/001.csv", index=False, encoding="utf-8-sig")

print("CSV файл сгенерирован: ./files/001.csv с 320+ записями и крупными доходами/расходами")