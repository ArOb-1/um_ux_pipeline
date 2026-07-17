"""
Генерация и сохранение отчетов в файлы
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .logger import logger


class ReportGenerator:
    """Генерация отчетов в разных форматах"""

    @staticmethod
    def _ensure_results_dir() -> Path:
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        return results_dir

    @staticmethod
    def to_markdown(result: Dict[str, Any], filename: str = "report.md") -> str:
        """Сохраняет отчет в Markdown"""
        results_dir = ReportGenerator._ensure_results_dir()
        filepath = results_dir / filename

        lines = []

        lines.append(f"# UMUX Pipeline Report")
        lines.append(f"*Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        lines.append("## Общая статистика")
        lines.append("| Метрика | Значение |")
        lines.append("|---------|----------|")
        lines.append(f"| Валидных записей | {result.get('total_valid', 0)} |")
        lines.append(f"| Отбраковано | {result.get('total_rejected', 0)} |")
        lines.append(f"| Время обработки | {result.get('processing_time', 0):.2f}с |")
        lines.append(f"| Обработано файлов | {len(result.get('files_processed', []))} |")
        lines.append("")

        rejection_stats = result.get('rejection_stats', {})
        if rejection_stats:
            lines.append("## Причины отбраковки")
            lines.append("| Причина | Количество |")
            lines.append("|---------|------------|")
            for reason, count in rejection_stats.items():
                lines.append(f"| {reason} | {count} |")
            lines.append("")

        aggregations = result.get('aggregations', {})
        overall = aggregations.get('overall', {})
        if overall:
            lines.append("## UMUX Статистика")
            lines.append("| Метрика | Значение |")
            lines.append("|---------|----------|")
            lines.append(f"| Средний UMUX | {overall.get('avg_umux', 0):.2f} |")
            lines.append(f"| Медиана | {overall.get('median_umux', 0):.2f} |")
            lines.append(f"| Стандартное отклонение | {overall.get('std_umux', 0):.2f} |")
            lines.append(f"| Минимум | {overall.get('min_umux', 0):.2f} |")
            lines.append(f"| Максимум | {overall.get('max_umux', 0):.2f} |")
            lines.append("")

        by_product = aggregations.get('by_product', [])
        if by_product:
            lines.append("## По продуктам")
            lines.append("| Продукт | Средний UMUX | Ответов |")
            lines.append("|---------|--------------|---------|")
            for p in by_product[:10]:
                lines.append(f"| {p.get('product', '')} | {p.get('avg_umux', 0):.2f} | {p.get('count', 0)} |")
            if len(by_product) > 10:
                lines.append(f"| ... и еще {len(by_product) - 10} продуктов | | |")
            lines.append("")

        by_month = aggregations.get('by_month', [])
        if by_month:
            lines.append("## По месяцам")
            lines.append("| Месяц | Средний UMUX | Ответов |")
            lines.append("|-------|--------------|---------|")
            for m in by_month:
                lines.append(f"| {m.get('month', '')} | {m.get('avg_umux', 0):.2f} | {m.get('count', 0)} |")
            lines.append("")

        by_platform = aggregations.get('by_platform', [])
        if by_platform:
            lines.append("## 📱 По платформам")
            lines.append("| Платформа | Средний UMUX | Ответов |")
            lines.append("|-----------|--------------|---------|")
            for p in by_platform:
                lines.append(f"| {p.get('platform', '')} | {p.get('avg_umux', 0):.2f} | {p.get('count', 0)} |")
            lines.append("")

        if result.get('files_processed'):
            lines.append("## Обработанные файлы")
            for f in result['files_processed']:
                lines.append(f"- `{f}`")
            lines.append("")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        logger.info('report saved filepath: ' + str(filepath))
        return str(filepath)

    @staticmethod
    def to_json(result: Dict[str, Any], filename: str = "report.json") -> str:
        """Сохраняет отчет в JSON"""
        results_dir = ReportGenerator._ensure_results_dir()
        filepath = results_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str, ensure_ascii=False)

        return str(filepath)

    @staticmethod
    def save_dashboard(html_content: str,
                       filename: str = "dashboard.html") -> str:
        """Сохраняет HTML дашборд"""
        results_dir = ReportGenerator._ensure_results_dir()
        filepath = results_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info('dashboard saved: ' + str(filepath))
        return str(filepath)
