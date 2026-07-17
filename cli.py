import argparse
import sys
import os
import asyncio
from pathlib import Path

from app.services.pipeline import create_async_pipeline
from app.utils import Console, ReportGenerator
from app.utils.logger import logger


sys.path.insert(0, str(Path(__file__).parent))


async def async_main(args):
    """Асинхронная главная функция"""

    if args.clear:
        logger.info("🗑️ Очистка базы данных по запросу пользователя")
        pipeline = create_async_pipeline()
        await pipeline.repository.clear()
        Console.success("База данных очищена")
        return

    if args.show:
        pipeline = create_async_pipeline()
        filters = {}
        if args.product:
            filters['product'] = args.product
        if args.platform:
            filters['platform'] = args.platform
        if args.month:
            filters['month'] = args.month
        
        aggregations = await pipeline.repository.get_aggregations(filters)
        
        if aggregations.get('total', 0) == 0:
            Console.warning("Нет данных в базе")
            return
        
        Console.header("📊 ДАННЫЕ ИЗ БАЗЫ")
        overall = aggregations.get('overall', {})
        Console.print_key_value("Всего записей", aggregations.get('total', 0))
        Console.print_key_value("Средний UMUX", f"{overall.get('avg_umux', 0):.2f}")
        
        by_product = aggregations.get('by_product', [])
        if by_product:
            Console.sub_header("По продуктам")
            for p in by_product[:10]:
                print(f"  • {p.get('product', '')}: {p.get('avg_umux', 0):.2f} ({p.get('count', 0)} ответов)")
        return
    
    # Проверка файлов
    if not args.files:
        Console.error("Не указаны файлы для обработки")
        return
    
    for file_path in args.files:
        if not os.path.exists(file_path):
            Console.error(f"Файл не найден: {file_path}")
            return
    
    # Запуск пайплайна
    logger.info(f"🚀 Запуск обработки файлов: {', '.join(args.files)}")
    
    # Создаем папку results
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Создаем пайплайн (он сам инициализирует БД при первом использовании)
    pipeline = create_async_pipeline()
    
    try:
        result = await pipeline.process(args.files)
        result_dict = result.to_dict()
        
        # Сохранение отчета
        ReportGenerator.to_markdown(result_dict)
        Console.success(f"Отчет: results/report.md")
        
        # Проверяем что дашборд создался
        dashboard_path = Path("results/dashboard.html")
        if dashboard_path.exists():
            Console.success(f"Дашборд: results/dashboard.html")
        else:
            Console.warning("Дашборд не создан")
        
        logger.info(f"✅ Пайплайн завершен. Валидных: {result.total_valid}, Отбраковано: {result.total_rejected}, Время: {result.processing_time:.2f}с")
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="UMUX Pipeline - обработка и анализ данных UMUX-Lite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python cli.py data/test_data.csv
  python cli.py --show
  python cli.py --clear
        """
    )
    
    parser.add_argument('files', nargs='*', help='Пути к CSV файлам')
    parser.add_argument('--db', type=str, default='sqlite:///umux.db', help='Путь к БД')
    parser.add_argument('--dashboard', type=str, default='dashboard.html', help='Путь к дашборду')
    parser.add_argument('--show', '-s', action='store_true', help='Показать данные из БД')
    parser.add_argument('--product', '-p', type=str, help='Фильтр по продукту')
    parser.add_argument('--platform', type=str, help='Фильтр по платформе')
    parser.add_argument('--month', type=str, help='Фильтр по месяцу')
    parser.add_argument('--clear', '-c', action='store_true', help='Очистить БД')
    parser.add_argument('--version', '-v', action='version', version='UMUX Pipeline 1.0.0')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем")
        sys.exit(0)


if __name__ == '__main__':
    main()
