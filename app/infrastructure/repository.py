import json
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text,
    select, func, and_, delete
)

from app.utils.logger import logger
from ..core.interfaces import IRepository


Base = declarative_base()


class Response(Base):
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(String(50), unique=True, nullable=False, index=True)
    submitted_at = Column(DateTime, nullable=False, index=True)
    product = Column(String(100), nullable=False, index=True)
    product_version = Column(String(50), nullable=False)
    platform = Column(String(20), nullable=False, index=True)
    country = Column(String(50))
    user_segment = Column(String(50))
    score1 = Column(Integer, nullable=False)
    score2 = Column(Integer, nullable=False)
    umux_score = Column(Float, nullable=False, index=True)
    month = Column(String(7), index=True)
    processed_at = Column(DateTime, default=datetime.utcnow)


class RejectedResponse(Base):
    __tablename__ = 'rejected_responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(String(50), index=True)
    submitted_at = Column(DateTime)
    product = Column(String(100))
    product_version = Column(String(50))
    platform = Column(String(20))
    country = Column(String(50))
    user_segment = Column(String(50))
    score1 = Column(Integer)
    score2 = Column(Integer)
    rejection_reason = Column(String(50), nullable=False, index=True)
    raw_data = Column(Text)
    processed_at = Column(DateTime, default=datetime.utcnow)


class AsyncSQLiteRepository(IRepository):
    """Асинхронная SQLite реализация репозитория"""

    def __init__(self, db_path: str = "sqlite:///umux.db"):
        async_db_path = db_path.replace("sqlite:///", "sqlite+aiosqlite:///")
        self.db_path = async_db_path
        self._engine = None
        self._async_session_maker = None
        logger.info("Асинхронный репозиторий инициализирован")

    async def _get_engine(self):
        if self._engine is None:
            self._engine = create_async_engine(
                self.db_path,
                echo=False
            )
        return self._engine

    async def _get_session(self) -> AsyncSession:
        engine = await self._get_engine()
        if self._async_session_maker is None:
            self._async_session_maker = async_sessionmaker(
                engine, 
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )
        return self._async_session_maker()

    async def init_db(self):
        engine = await self._get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных инициализирована")

    async def save_valid(self, df: pd.DataFrame) -> int:
        """Сохраняет валидные ответы с обработкой дубликатов"""
        if df.empty:
            return 0

        session = await self._get_session()
        try:
            count = 0
            for _, row in df.iterrows():
                response_id = str(row['response_id'])

                stmt = select(Response).where(Response.response_id == response_id)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    existing.submitted_at = row['submitted_at']
                    existing.product = str(row['product'])
                    existing.product_version = str(row['product_version'])
                    existing.platform = str(row.get('platform', 'unknown'))
                    existing.country = str(row.get('country', 'unknown'))
                    existing.user_segment = str(row.get('user_segment', 'unknown'))
                    existing.score1 = int(row['score1'])
                    existing.score2 = int(row['score2'])
                    existing.umux_score = float(row['umux_score'])
                    existing.month = row['submitted_at'].strftime('%Y-%m') if hasattr(row['submitted_at'], 'strftime') else str(row['submitted_at'])[:7]
                    existing.processed_at = datetime.utcnow()
                else:
                    response = Response(
                        response_id=response_id,
                        submitted_at=row['submitted_at'],
                        product=str(row['product']),
                        product_version=str(row['product_version']),
                        platform=str(row.get('platform', 'unknown')),
                        country=str(row.get('country', 'unknown')),
                        user_segment=str(row.get('user_segment', 'unknown')),
                        score1=int(row['score1']),
                        score2=int(row['score2']),
                        umux_score=float(row['umux_score']),
                        month=row['submitted_at'].strftime('%Y-%m') if hasattr(row['submitted_at'], 'strftime') else str(row['submitted_at'])[:7],
                        processed_at=datetime.utcnow()
                    )
                    session.add(response)
                count += 1

            await session.commit()
            logger.info(f"Сохранено {count} валидных записей (обновлены существующие)")
            return count

        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка сохранения: {e}")
            raise e
        finally:
            await session.close()

    async def save_rejected(self, df: pd.DataFrame) -> int:
        """Сохраняет отбракованные записи"""
        if df.empty:
            return 0

        session = await self._get_session()
        try:
            count = 0
            for _, row in df.iterrows():
                score1 = row.get('score1')
                if pd.notna(score1) and score1 is not None:
                    try:
                        score1 = int(float(score1))
                    except (ValueError, TypeError):
                        score1 = None
                else:
                    score1 = None

                score2 = row.get('score2')
                if pd.notna(score2) and score2 is not None:
                    try:
                        score2 = int(float(score2))
                    except (ValueError, TypeError):
                        score2 = None
                else:
                    score2 = None

                rejected = RejectedResponse(
                    response_id=str(row.get('response_id', '')) if pd.notna(row.get('response_id')) else '',
                    submitted_at=row.get('submitted_at') if pd.notna(row.get('submitted_at')) else None,
                    product=str(row.get('product', '')) if pd.notna(row.get('product')) else '',
                    product_version=str(row.get('product_version', '')) if pd.notna(row.get('product_version')) else '',
                    platform=str(row.get('platform', '')) if pd.notna(row.get('platform')) else '',
                    country=str(row.get('country', '')) if pd.notna(row.get('country')) else '',
                    user_segment=str(row.get('user_segment', '')) if pd.notna(row.get('user_segment')) else '',
                    score1=score1,
                    score2=score2,
                    rejection_reason=str(row.get('rejection_reason', 'unknown')),
                    raw_data=row.to_json() if hasattr(row, 'to_json') else json.dumps(row.to_dict(), default=str),
                    processed_at=datetime.utcnow()
                )
                session.add(rejected)
                count += 1

            await session.commit()
            logger.info(f"Сохранено {count} отбракованных записей")
            return count

        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка сохранения rejected: {e}")
            raise e
        finally:
            await session.close()

    async def get_aggregations(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session = await self._get_session()
        try:
            query = select(Response)
            conditions = []

            if filters:
                if 'product' in filters:
                    conditions.append(Response.product == filters['product'])
                if 'platform' in filters:
                    conditions.append(Response.platform == filters['platform'])
                if 'month' in filters:
                    conditions.append(Response.month == filters['month'])
                if 'start_date' in filters:
                    conditions.append(Response.submitted_at >= filters['start_date'])
                if 'end_date' in filters:
                    conditions.append(Response.submitted_at <= filters['end_date'])

            if conditions:
                query = query.where(and_(*conditions))

            count_query = select(func.count()).select_from(Response)
            if conditions:
                count_query = count_query.where(and_(*conditions))

            total = await session.scalar(count_query)

            if total == 0:
                return {'total': 0, 'overall': {'avg_umux': 0, 'count': 0}}

            stats_query = select(
                func.avg(Response.umux_score).label('avg'),
                func.stddev(Response.umux_score).label('std'),
                func.min(Response.umux_score).label('min'),
                func.max(Response.umux_score).label('max')
            )
            if conditions:
                stats_query = stats_query.where(and_(*conditions))

            stats_result = await session.execute(stats_query)
            stats_row = stats_result.one()

            result = {
                'total': total,
                'overall': {
                    'avg_umux': float(stats_row[0] or 0),
                    'std_umux': float(stats_row[1] or 0),
                    'min_umux': float(stats_row[2] or 0),
                    'max_umux': float(stats_row[3] or 0),
                    'count': total
                }
            }

            product_query = select(
                Response.product,
                func.avg(Response.umux_score).label('avg'),
                func.count(Response.id).label('count'),
                func.stddev(Response.umux_score).label('std')
            )
            if conditions:
                product_query = product_query.where(and_(*conditions))
            product_query = product_query.group_by(Response.product)

            product_result = await session.execute(product_query)
            result['by_product'] = [
                {
                    'product': p[0],
                    'avg_umux': float(p[1]),
                    'count': p[2],
                    'std_umux': float(p[3]) if p[3] else 0
                }
                for p in product_result.all()
            ]

            product_version_query = select(
                Response.product,
                Response.product_version,
                func.avg(Response.umux_score).label('avg'),
                func.count(Response.id).label('count')
            )
            if conditions:
                product_version_query = product_version_query.where(and_(*conditions))
            product_version_query = product_version_query.group_by(Response.product, Response.product_version)

            product_version_result = await session.execute(product_version_query)
            result['by_product_version'] = [
                {
                    'product': p[0],
                    'version': p[1],
                    'avg_umux': float(p[2]),
                    'count': p[3]
                }
                for p in product_version_result.all()
            ]

            month_query = select(
                Response.month,
                func.avg(Response.umux_score).label('avg'),
                func.count(Response.id).label('count')
            )
            if conditions:
                month_query = month_query.where(and_(*conditions))
            month_query = month_query.group_by(Response.month).order_by(Response.month)

            month_result = await session.execute(month_query)
            result['by_month'] = [
                {
                    'month': m[0],
                    'avg_umux': float(m[1]),
                    'count': m[2]
                }
                for m in month_result.all()
            ]

            platform_query = select(
                Response.platform,
                func.avg(Response.umux_score).label('avg'),
                func.count(Response.id).label('count')
            )
            if conditions:
                platform_query = platform_query.where(and_(*conditions))
            platform_query = platform_query.group_by(Response.platform)

            platform_result = await session.execute(platform_query)
            result['by_platform'] = [
                {
                    'platform': p[0],
                    'avg_umux': float(p[1]),
                    'count': p[2]
                }
                for p in platform_result.all()
            ]

            return result

        except Exception as e:
            logger.error(f"Ошибка получения агрегаций: {e}")
            return {'total': 0, 'overall': {'avg_umux': 0, 'count': 0}}
        finally:
            await session.close()

    async def get_rejection_stats(self) -> Dict[str, int]:
        session = await self._get_session()
        try:
            query = select(
                RejectedResponse.rejection_reason,
                func.count(RejectedResponse.id)
            ).group_by(RejectedResponse.rejection_reason)

            result = await session.execute(query)
            return {r[0]: r[1] for r in result.all()}
        except Exception as e:
            logger.error(f"Ошибка получения статистики отбраковки: {e}")
            return {}
        finally:
            await session.close()

    async def clear(self) -> None:
        session = await self._get_session()
        try:
            await session.execute(delete(Response))
            await session.execute(delete(RejectedResponse))
            await session.commit()
            logger.info("База данных очищена")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка очистки: {e}")
            raise e
        finally:
            await session.close()

    async def get_product_list(self) -> List[str]:
        session = await self._get_session()
        try:
            query = select(Response.product).distinct()
            result = await session.execute(query)
            return [r[0] for r in result.all()]
        except Exception as e:
            logger.error(f"Ошибка получения списка продуктов: {e}")
            return []
        finally:
            await session.close()
