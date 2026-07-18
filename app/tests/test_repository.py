import pytest
import pandas as pd
import os

from app.infrastructure.repository import AsyncSQLiteRepository


class TestRepository:
    """Тесты репозитория"""

    @pytest.mark.asyncio
    async def test_save_and_get_aggregations(self):
        """Проверка сохранения и получения агрегаций"""
        repo = AsyncSQLiteRepository("sqlite:///test.db")
        await repo.init_db()

        try:
            df = pd.DataFrame({
                'response_id': ['1', '2', '3'],
                'submitted_at': pd.to_datetime(['2024-01-01', '2024-01-15', '2024-02-01']),
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

            await repo.save_valid(df)
            aggregations = await repo.get_aggregations()

            assert aggregations['total'] == 3
            assert aggregations['overall']['avg_umux'] == 70.0
            assert len(aggregations['by_product']) == 2
            assert len(aggregations['by_month']) == 2

            months = [m['month'] for m in aggregations['by_month']]
            assert '2024-01' in months
            assert '2024-02' in months

        finally:
            await repo.clear()
            if os.path.exists("test.db"):
                os.remove("test.db")

    @pytest.mark.asyncio
    async def test_clear(self):
        """Проверка очистки данных"""
        repo = AsyncSQLiteRepository("sqlite:///test_clear.db")
        await repo.init_db()

        try:
            df = pd.DataFrame({
                'response_id': ['1'],
                'submitted_at': pd.to_datetime(['2024-01-01']),
                'product': ['A'],
                'product_version': ['1.0'],
                'platform': ['web'],
                'country': ['US'],
                'user_segment': ['premium'],
                'score1': [5],
                'score2': [4],
                'umux_score': [90],
                'month': ['2024-01']
            })

            await repo.save_valid(df)
            aggregations = await repo.get_aggregations()
            assert aggregations['total'] == 1

            await repo.clear()
            aggregations = await repo.get_aggregations()
            assert aggregations['total'] == 0

        finally:
            await repo.clear()
            if os.path.exists("test_clear.db"):
                os.remove("test_clear.db")
