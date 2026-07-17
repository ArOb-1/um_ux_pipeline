from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.api.routes import router
from app.infrastructure.repository import AsyncSQLiteRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan для инициализации и очистки ресурсов"""
    # Startup
    logger.info("🚀 Запуск приложения...")
    
    # Инициализация БД (создание таблиц если их нет)
    repo = AsyncSQLiteRepository()
    await repo.init_db()
    
    logger.info("✅ Приложение запущено")
    yield
    
    # Shutdown
    logger.info("👋 Остановка приложения...")


# Создаем приложение
app = FastAPI(
    title="UMUX Pipeline API",
    description="API для обработки и визуализации UMUX-Lite данных",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "service": "UMUX Pipeline API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api/v1"
        }
    }


@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "umux-pipeline"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
