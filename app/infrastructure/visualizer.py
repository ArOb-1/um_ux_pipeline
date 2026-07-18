import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any
import base64
from pathlib import Path

from ..core.interfaces import IVisualizer
from app.utils.logger import logger


class PlotlyVisualizer(IVisualizer):
    """Визуализатор с использованием Plotly"""

    PLATFORM_COLORS = {
        'web': '#1f77b4',
        'android': '#ff7f0e',
        'ios': '#2ca02c'
    }

    def __init__(self, theme: str = 'plotly_white'):
        self.theme = theme

    def create_dashboard(self,
                         df: pd.DataFrame,
                         aggregations: Dict[str, Any]) -> Dict[str, str]:
        """Создает дашборд с графиками"""
        visualizations = {}

        if df.empty or 'umux_score' not in df.columns:
            logger.warning("Нет данных для визуализации")
            return visualizations

        try:
            logger.info("Создание product_chart")
            fig1 = self._create_product_chart(aggregations)
            visualizations['product_chart'] = self._fig_to_base64(fig1)

            logger.info("Создание monthly trend")
            fig2 = self._create_monthly_trend(aggregations)
            visualizations['monthly_trend'] = self._fig_to_base64(fig2)

            logger.info("Создание platform chart")
            fig3 = self._create_platform_chart(aggregations)
            visualizations['platform_chart'] = self._fig_to_base64(fig3)

            logger.info("Создание distribution")
            fig4 = self._create_distribution(df)
            visualizations['distribution'] = self._fig_to_base64(fig4)

            logger.info(f"Создано {len(visualizations)} графиков")

        except Exception as e:
            logger.error(f"Ошибка создания дашборда: {e}")

        return visualizations

    def _create_product_chart(self, aggregations: Dict[str, Any]) -> go.Figure:
        """График среднего UMUX по продуктам"""
        data = aggregations.get('by_product', [])

        if not data:
            return go.Figure()

        df = pd.DataFrame(data)
        df = df.sort_values('avg_umux', ascending=False)

        colors = []
        for val in df['avg_umux']:
            if val >= 80:
                colors.append('#2ca02c')
            elif val >= 60:
                colors.append('#ff7f0e')
            else:
                colors.append('#d62728')

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df['product'],
            y=df['avg_umux'],
            text=df['avg_umux'].round(1),
            textposition='auto',
            marker_color=colors,
            name='Средний UMUX',
            error_y=dict(
                type='data',
                array=df.get('std_umux', [0] * len(df)),
                visible=True
            )
        ))

        fig.update_layout(
            title='Средний UMUX по продуктам',
            xaxis_title='Продукт',
            yaxis_title='UMUX Score',
            template=self.theme,
            height=400,
            showlegend=False
        )

        fig.add_hline(y=80,
                      line_dash="dash",
                      line_color="#2ca02c",
                      annotation_text="Целевой уровень (80)")
        fig.add_hline(y=60,
                      line_dash="dash",
                      line_color="#d62728",
                      annotation_text="Критический уровень (60)")

        return fig

    def _create_monthly_trend(self, aggregations: Dict[str, Any]) -> go.Figure:
        """Динамика UMUX по месяцам"""
        data = aggregations.get('by_month', [])

        if not data:
            return go.Figure()

        df = pd.DataFrame(data)
        df = df.sort_values('month')

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['avg_umux'],
            mode='lines+markers',
            name='Средний UMUX',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10, color='#1f77b4')
        ))

        fig.update_layout(
            title='Динамика UMUX по месяцам',
            xaxis_title='Месяц',
            yaxis_title='UMUX Score',
            template=self.theme,
            height=400,
            hovermode='x unified'
        )

        fig.add_hline(y=80,
                      line_dash="dash",
                      line_color="#2ca02c",
                      annotation_text="Целевой уровень (80)")
        fig.add_hline(y=60,
                      line_dash="dash",
                      line_color="#d62728",
                      annotation_text="Критический уровень (60)")

        return fig

    def _create_platform_chart(self,
                               aggregations: Dict[str, Any]) -> go.Figure:
        """Сравнение по платформам с одинаковыми цветами"""
        data = aggregations.get('by_platform', [])

        if not data:
            return go.Figure()

        df = pd.DataFrame(data)

        colors = []
        for p in df['platform']:
            p_lower = p.lower()
            if p_lower in self.PLATFORM_COLORS:
                colors.append(self.PLATFORM_COLORS[p_lower])
            else:
                colors.append('#999999')

        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'bar'}, {'type': 'pie'}]],
            subplot_titles=('Средний UMUX', 'Распределение ответов')
        )

        fig.add_trace(
            go.Bar(
                x=df['platform'],
                y=df['avg_umux'],
                text=df['avg_umux'].round(1),
                textposition='auto',
                marker_color=colors,
                name='Средний UMUX'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Pie(
                labels=df['platform'],
                values=df['count'],
                hole=0.3,
                textinfo='label+percent',
                marker=dict(colors=colors),
                name='Распределение'
            ),
            row=1, col=2
        )

        fig.update_layout(
            title='Сравнение по платформам',
            template=self.theme,
            height=400,
            showlegend=False
        )

        return fig

    def _create_distribution(self, df: pd.DataFrame) -> go.Figure:
        """Распределение UMUX скора (только гистограмма)"""
        if 'umux_score' not in df.columns:
            return go.Figure()

        scores = df['umux_score'].dropna()

        if len(scores) == 0:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=20,
            marker_color='#1f77b4',
            name='Распределение'
        ))

        mean_val = scores.mean()
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="#d62728",
            annotation_text=f"Средний: {mean_val:.1f}"
        )

        fig.update_layout(
            title='Распределение UMUX скора',
            xaxis_title='UMUX Score',
            yaxis_title='Количество ответов',
            template=self.theme,
            height=400,
            showlegend=False
        )

        return fig

    def _fig_to_base64(self, fig: go.Figure) -> str:
        """Конвертирует фигуру Plotly в base64 строку"""
        try:
            img_bytes = fig.to_image(format="png",
                                     width=800,
                                     height=500,
                                     scale=1)
            return base64.b64encode(img_bytes).decode('ascii')
        except Exception as e:
            logger.warning(f"Не удалось экспортировать PNG: {e}")
            return ""

    def save_dashboard(self,
                       visualizations: Dict[str, str],
                       filename: str = "dashboard.html") -> str:
        """Сохраняет дашборд как HTML файл и возвращает HTML контент"""
        if not visualizations:
            logger.warning("Нет визуализаций для сохранения")
            return ""

        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        filepath = results_dir / filename

        logger.info(f"Сохранение дашборда в {filepath}")

        try:
            html_parts = []

            for name, b64_data in visualizations.items():
                if not b64_data:
                    continue

                html_parts.append(
                    f'<div class="chart"><h3>{name}</h3>'
                    f'<img src="data:image/png;base64,{b64_data}" style="max-width:100%"/>'
                    f'</div>'
                )

            if html_parts:
                html_template = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>UMUX Dashboard</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                        .container {{ max-width: 1200px; margin: 0 auto; }}
                        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                        .header h1 {{ margin: 0; }}
                        .chart {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: auto; }}
                        .row {{ display: flex; flex-wrap: wrap; gap: 20px; }}
                        .col {{ flex: 1; min-width: 400px; }}
                        .footer {{ text-align: center; color: #7f8c8d; margin-top: 20px; padding: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>📊 UMUX Dashboard</h1>
                            <p>Анализ пользовательского опыта по продуктам</p>
                        </div>
                        {''.join(html_parts)}
                        <div class="footer">
                            <p>Сгенерировано {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                    </div>
                </body>
                </html>
                """

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_template)
                logger.info(f"Дашборд сохранен в {filepath}")
                return html_template
            else:
                logger.warning("Не удалось сохранить дашборд")
                return ""

        except Exception as e:
            logger.error(f"Ошибка сохранения дашборда: {e}")
            return ""
