import pytest
import os
import tempfile

from app.services.pipeline import create_async_pipeline


class TestPipeline:
    """Интеграционные тесты пайплайна"""

    @pytest.mark.asyncio
    async def test_pipeline_process(self):
        """Проверка работы пайплайна"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("response_id,submitted_at,product,product_version,platform,country,user_segment,score1,score2\n")
            f.write("1,2024-01-01 10:00:00,Product A,1.0.0,Web,US,premium,5,4\n")
            f.write("2,2024-01-02 11:00:00,Product B,2.0.0,Android,UK,free,4,3\n")
            temp_file = f.name

        try:
            pipeline = create_async_pipeline()
            result = await pipeline.process([temp_file])

            assert result.total_valid == 2
            assert result.total_rejected == 0
            assert result.aggregations['overall']['total_responses'] == 2
        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_pipeline_with_invalid_data(self):
        """Проверка работы пайплайна с невалидными данными"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("response_id,submitted_at,product,product_version,platform,score1,score2\n")
            f.write("1,invalid_date,Product A,1.0.0,Web,5,4\n")
            f.write("2,2024-01-02 11:00:00,Product B,2.0.0,Windows,4,3\n")
            temp_file = f.name

        try:
            pipeline = create_async_pipeline()
            result = await pipeline.process([temp_file])

            assert result.total_valid == 0
            assert result.total_rejected == 2
            assert 'invalid_date' in result.rejection_stats
            assert 'invalid_platform' in result.rejection_stats
        finally:
            os.unlink(temp_file)
