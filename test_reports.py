import os
import pandas as pd
import pytest
from reports import spending_by_category, spending_by_weekday, spending_by_workday

@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    return pd.DataFrame([
        {"date": "2023-10-01", "description": "Супермаркеты", "amount": "100.0"},
        {"date": "2023-10-02", "description": "Фастфуд", "amount": "200.0"},
        {"date": "2023-10-07", "description": "Супермаркеты", "amount": "300.0"},
        {"date": "2023-12-15", "description": "Развлечения", "amount": "500.0"},
        {"date": "2023-05-01", "description": "Супермаркеты", "amount": "1000.0"},
    ])

def test_spending_by_category(sample_transactions: pd.DataFrame) -> None:
    result = spending_by_category(sample_transactions, "Супермаркеты", "2023-12-31")
    assert len(result) == 2
    assert result["amount"].tolist() == ["100.0", "300.0"]

def test_spending_by_weekday(sample_transactions: pd.DataFrame) -> None:
    result = spending_by_weekday(sample_transactions, "2023-12-31")
    assert not result.empty
    assert "weekday" in result.columns
    assert "amount_float" in result.columns

def test_spending_by_workday(sample_transactions: pd.DataFrame) -> None:
    result = spending_by_workday(sample_transactions, "2023-12-31")
    assert not result.empty
    assert "day_type" in result.columns
    assert "amount_float" in result.columns

def test_report_decorator_file_creation() -> None:
    assert os.path.exists("logs/category_report.txt")