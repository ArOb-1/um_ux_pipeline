from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
import tempfile
import os

from app.services.pipeline import create_async_pipeline
from app.api.schemas import UploadResponse, AggregationResponse
from app.utils.logger import logger

router = APIRouter()

pipeline = create_async_pipeline()


@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Загрузка и обработка CSV файлов"""
    temp_files = []

    try:
        for file in files:
            if not file.filename.endswith('.csv'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Неподдерживаемый формат: {file.filename}. Ожидается CSV"
                )

            content = await file.read()
            if not content or len(content.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Файл {file.filename} пуст"
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                tmp.write(content)
                temp_files.append(tmp.name)

        result = await pipeline.process(temp_files)

        return UploadResponse(
            status="success",
            total_valid=result.total_valid,
            total_rejected=result.total_rejected,
            rejection_stats=result.rejection_stats,
            processing_time=result.processing_time,
            files_processed=result.files_processed
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for f in temp_files:
            try:
                os.unlink(f)
            except Exception as e:
                logger.error(str(e))


@router.get("/results", response_model=AggregationResponse)
async def get_results(
    product: Optional[str] = Query(None, description="Фильтр по продукту"),
    platform: Optional[str] = Query(None, description="Фильтр по платформе"),
    month: Optional[str] = Query(None, description="Фильтр по месяцу (YYYY-MM)")
):
    """Получение агрегированных результатов"""
    try:
        filters = {}
        if product:
            filters['product'] = product
        if platform:
            filters['platform'] = platform
        if month:
            filters['month'] = month

        aggregations = await pipeline.repository.get_aggregations(filters)

        return AggregationResponse(
            status="success",
            total=aggregations.get('total', 0),
            overall=aggregations.get('overall', {}),
            by_product=aggregations.get('by_product', []),
            by_product_version=aggregations.get('by_product_version', []),
            by_month=aggregations.get('by_month', []),
            by_platform=aggregations.get('by_platform', [])
        )

    except Exception as e:
        logger.error(f"Ошибка получения результатов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard():
    """Получение HTML дашборда"""
    possible_paths = ["results/dashboard.html", "dashboard.html"]

    for path in possible_paths:
        if os.path.exists(path):
            return FileResponse(
                path,
                media_type="text/html",
                filename="dashboard.html"
            )

    raise HTTPException(
        status_code=404,
        detail="Дашборд не найден. Сначала загрузите данные через /upload"
    )


@router.get("/products")
async def get_products():
    """Получение списка всех продуктов"""
    try:
        products = await pipeline.repository.get_product_list()
        return {"status": "success", "products": products}
    except Exception as e:
        logger.error(f"Ошибка получения списка продуктов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_data():
    """Очистка всех данных"""
    try:
        await pipeline.repository.clear()
        return {"status": "success", "message": "Все данные очищены"}
    except Exception as e:
        logger.error(f"Ошибка очистки: {e}")
        raise HTTPException(status_code=500, detail=str(e))
