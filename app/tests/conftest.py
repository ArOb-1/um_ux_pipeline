import pytest
import tempfile
import os
import pandas as pd

from httpx import AsyncClient, ASGITransport
from pathlib import Path
from typing import AsyncGenerator

from app.infrastructure.repository import AsyncSQLiteRepository
from app.main import app


@pytest.fixture
def temp_csv():
    """Создает временный CSV файл и возвращает его путь"""
    files = []

    def _create_csv(content: str, filename: str = None) -> str:
        if filename:
            filepath = Path(f"data/{filename}")
            filepath.parent.mkdir(exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            files.append(str(filepath))
            return str(filepath)
        else:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(content)
                temp_file = f.name
            files.append(temp_file)
            return temp_file

    yield _create_csv

    for f in files:
        try:
            os.unlink(f)
        except OSError:
            pass


@pytest.fixture
def sample_valid_data():
    """Возвращает валидный DataFrame для тестов"""
    return pd.DataFrame({
        'response_id': ['1', '2', '3'],
        'submitted_at': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        'product': ['A', 'A', 'B'],
        'product_version': ['1.0', '1.0', '2.0'],
        'platform': ['web', 'android', 'web'],
        'country': ['US', 'UK', 'DE'],
        'user_segment': ['premium', 'free', 'premium'],
        'score1': [5, 4, 3],
        'score2': [4, 3, 2],
        'umux_score': [90, 70, 50],
        'month': ['2024-01', '2024-01', '2024-02']
    })


@pytest.fixture
async def test_repository():
    """Создает временную БД для тестов"""
    repo = AsyncSQLiteRepository("sqlite:///test.db")
    await repo.init_db()
    yield repo
    await repo.clear()
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def event_loop():
    """Создает event loop для асинхронных тестов"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client() -> AsyncGenerator:
    """Создает асинхронный клиент для тестирования API"""
    repo = AsyncSQLiteRepository()
    await repo.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,
                           base_url="http://test") as client:
        yield client

    await repo.clear()


@pytest.fixture
def test_csv_file():
    """Создает тестовый CSV файл"""
    csv_content = """response_id,submitted_at,product,product_version,platform,country,user_segment,score1,score2
RESP-001,2024-01-15 10:30:00,Product A,1.0.0,Web,US,premium,5,4
RESP-002,2024-01-15 11:00:00,Product A,1.0.0,Android,UK,free,4,3
RESP-003,2024-01-16 09:00:00,Product B,2.1.0,iOS,DE,premium,5,5
RESP-004,2024-01-17 14:30:00,Product A,1.0.1,web,FR,enterprise,4,4
RESP-005,2024-01-18 08:45:00,Product C,3.0.0,Web,US,free,5,3"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_file = f.name

    yield temp_file

    try:
        os.unlink(temp_file)
    except OSError:
        pass
