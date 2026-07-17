import pandas as pd
from typing import List, Optional, Dict, Any
import time
import logging

from ..core.interfaces import (
    IDataLoader, IValidator, ICalculator,
    IAggregator, IRepository, IVisualizer, IPipeline
)
from ..core.models import PipelineResult
from ..infrastructure.loaders import CSVLoader
from ..domain.validators import UMUXValidator
from ..domain.calculators import UMUXCalculator
from ..domain.aggregators import UMUXAggregator
from ..infrastructure.repository import AsyncSQLiteRepository
from ..infrastructure.visualizer import PlotlyVisualizer

logger = logging.getLogger(__name__)


class AsyncPipelineService(IPipeline):
    """Асинхронный сервис пайплайна обработки данных"""

    def __init__(
        self,
        loader: Optional[IDataLoader] = None,
        validator: Optional[IValidator] = None,
        calculator: Optional[ICalculator] = None,
        aggregator: Optional[IAggregator] = None,
        repository: Optional[IRepository] = None,
        visualizer: Optional[IVisualizer] = None
    ):
        self.loader = loader or CSVLoader()
        self.validator = validator or UMUXValidator()
        self.calculator = calculator or UMUXCalculator()
        self.aggregator = aggregator or UMUXAggregator()
        self.repository = repository or AsyncSQLiteRepository()
        self.visualizer = visualizer or PlotlyVisualizer()
        self._initialized = False
        logger.info('Пайплайн инициализирован')

    async def _ensure_initialized(self):
        """Убеждается, что БД инициализирована"""
        if not self._initialized:
            if hasattr(self.repository, 'init_db'):
                await self.repository.init_db()
            self._initialized = True
        logger.info('База данных инициализирована')

    async def process(self, file_paths: List[str]) -> PipelineResult:
        """Асинхронная обработка файлов"""
        await self._ensure_initialized()
        logger.info('Запущен пайплайн')

        start_time = time.time()
        result = PipelineResult()

        all_valid_dfs = []
        all_rejected_dfs = []

        for file_path in file_paths:
            logger.info(f"Обработка файла: {file_path}")
            result.files_processed.append(file_path)

            df = self.loader.load(file_path)
            if df is None or df.empty:
                logger.error(f"Файл {file_path} пуст или не загружен")
                result.errors.append(f"Не удалось загрузить: {file_path}")
                continue

            logger.info(f"Загружено {len(df)} строк из {file_path}")

            valid_df, invalid_df = self.validator.validate(df)

            if not invalid_df.empty:
                all_rejected_dfs.append(invalid_df)
                logger.info(f"Отбраковано {len(invalid_df)} записей")

            if valid_df.empty:
                logger.warning(f"Нет валидных данных в {file_path}")
                continue

            valid_df = self.validator.normalize(valid_df)
            valid_df = self.calculator.calculate(valid_df)

            all_valid_dfs.append(valid_df)
            logger.info(f"Валидных записей: {len(valid_df)}")

        if all_valid_dfs:
            combined_valid = pd.concat(all_valid_dfs, ignore_index=True)

            valid_count = await self.repository.save_valid(combined_valid)
            result.total_valid = valid_count

            aggregations = self.aggregator.aggregate(combined_valid)
            result.aggregations = aggregations

            visualizations = (self.
                              visualizer.
                              create_dashboard(combined_valid, aggregations))
            result.visualizations = visualizations

            html_content = self.visualizer.save_dashboard(visualizations)
            result.visualizations['html'] = html_content

        if all_rejected_dfs:
            combined_rejected = pd.concat(all_rejected_dfs, ignore_index=True)
            rejected_count = await (self.
                                    repository.
                                    save_rejected(combined_rejected))
            result.total_rejected = rejected_count
            result.rejection_stats = self.validator.get_rejection_stats()

        result.processing_time = time.time() - start_time

        logger.info(f"Пайплайн завершен за {result.processing_time:.2f}с")
        logger.info(f"Валидных: {result.total_valid}")
        logger.info(f"Отбраковано: {result.total_rejected}")

        return result

    async def process_dataframe(self, df: pd.DataFrame) -> PipelineResult:
        """Обрабатывает DataFrame напрямую"""
        await self._ensure_initialized()
        logger.info('Обработка DataFrame')

        start_time = time.time()
        result = PipelineResult()

        try:
            valid_df, invalid_df = self.validator.validate(df)

            if not invalid_df.empty:
                await self.repository.save_rejected(invalid_df)
                result.total_rejected = len(invalid_df)
                result.rejection_stats = self.validator.get_rejection_stats()

            if valid_df.empty:
                result.aggregations = self._empty_aggregations()
                result.processing_time = time.time() - start_time
                return result

            valid_df = self.validator.normalize(valid_df)
            valid_df = self.calculator.calculate(valid_df)

            valid_count = await self.repository.save_valid(valid_df)
            result.total_valid = valid_count

            aggregations = self.aggregator.aggregate(valid_df)
            result.aggregations = aggregations

            visualizations = (self.
                              visualizer.
                              create_dashboard(valid_df, aggregations))
            result.visualizations = visualizations

            html_content = self.visualizer.save_dashboard(visualizations)
            result.visualizations['html'] = html_content

        except Exception as e:
            logger.error(f"Ошибка обработки DataFrame: {e}")
            result.errors.append(str(e))
            result.aggregations = self._empty_aggregations()

        result.processing_time = time.time() - start_time
        return result

    def _empty_aggregations(self) -> Dict[str, Any]:
        return {
            'overall': {
                'total_responses': 0,
                'avg_umux': 0,
                'std_umux': 0,
                'min_umux': 0,
                'max_umux': 0,
                'median_umux': 0
            },
            'by_product': [],
            'by_product_version': [],
            'by_month': [],
            'by_platform': []
        }


def create_async_pipeline() -> AsyncPipelineService:
    """Фабрика для создания асинхронного пайплайна"""
    return AsyncPipelineService(
        loader=CSVLoader(),
        validator=UMUXValidator(min_year=2020, max_year=2026),
        calculator=UMUXCalculator(),
        aggregator=UMUXAggregator(),
        repository=AsyncSQLiteRepository(),
        visualizer=PlotlyVisualizer()
    )
