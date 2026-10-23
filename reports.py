import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

os.makedirs("logs", exist_ok=True)

reports_logger = logging.getLogger("reports")
reports_logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/reports.log", mode="w", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
if not reports_logger.handlers:
    reports_logger.addHandler(handler)


def report_decorator(filename: Optional[str] = None) -> Callable:
    """Декоратор для сохранения результатов отчетов в файл или лог."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            output = result.to_string() if isinstance(result, pd.DataFrame) else str(result)
            log_message = f"Отчет от функции {func.__name__}:\n{output}"

            if filename:
                with open(filename, "a", encoding="utf-8") as file:
                    file.write(log_message + "\n" + "-" * 50 + "\n")
            else:
                reports_logger.info(log_message)
            return result
        return wrapper

    if callable(filename):
        func = filename
        filename = "default_report.txt"
        return decorator(func)
    return decorator


def _get_transaction_amount(transaction: pd.Series) -> float:
    """Вспомогательная функция: достает сумму из разных форматов (JSON/CSV)."""
    try:
        if isinstance(transaction.get("operationAmount"), dict):
            return float(transaction["operationAmount"]["amount"])
        return float(str(transaction.get("amount")).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


@report_decorator(filename="logs/category_report.txt")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние 3 месяца."""
    target_date = pd.to_datetime(date) if date else pd.Timestamp.now()
    start_date = target_date - pd.DateOffset(months=3)
    df = transactions.copy()
    df["date"] = pd.to_datetime(df["date"])
    mask = (df["date"] >= start_date) & (df["date"] <= target_date)
    filtered_df = df[mask]
    cat_mask = filtered_df["description"].str.contains(category, case=False, na=False)
    return filtered_df[cat_mask]


@report_decorator()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает средние траты по дням недели за последние 3 месяца."""
    target_date = pd.to_datetime(date) if date else pd.Timestamp.now()
    start_date = target_date - pd.DateOffset(months=3)
    df = transactions.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["amount_float"] = df.apply(_get_transaction_amount, axis=1)
    mask = (df["date"] >= start_date) & (df["date"] <= target_date)
    filtered_df = df[mask].copy()
    filtered_df["weekday"] = filtered_df["date"].dt.day_name()
    return filtered_df.groupby("weekday")["amount_float"].mean().reset_index()


@report_decorator()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает средние траты в рабочий и выходной день за последние 3 месяца."""
    target_date = pd.to_datetime(date) if date else pd.Timestamp.now()
    start_date = target_date - pd.DateOffset(months=3)
    df = transactions.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["amount_float"] = df.apply(_get_transaction_amount, axis=1)
    mask = (df["date"] >= start_date) & (df["date"] <= target_date)
    filtered_df = df[mask].copy()
    
    filtered_df["day_type"] = filtered_df["date"].dt.day_of_week.apply(
        lambda x: "Рабочий день" if x < 5 else "Выходной день"
    )
    
    return filtered_df.groupby("day_type")["amount_float"].mean().reset_index()