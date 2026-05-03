import pandas as pd

def export_to_excel(df: pd.DataFrame, summary: dict, path: str):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:

        # Операции
        df.to_excel(writer, sheet_name="Операции", index=False)

        # Сводка
        summary_df = pd.DataFrame([
            {"Показатель": "доход", "Значение": summary["доход"]},
            {"Показатель": "расход", "Значение": summary["расход"]},
            {"Показатель": "прибыль", "Значение": summary["прибыль"]},

        ])

        summary_df.to_excel(writer, sheet_name="Сводка", index=False)

        # Расход по категориям
        category_df = pd.DataFrame(
            list(summary["расход по категориям"].items()),
            columns=["Категория", "Сумма"]
        )

        category_df.to_excel(writer, sheet_name="Категории", index=False)