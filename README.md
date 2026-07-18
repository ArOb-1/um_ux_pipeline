# UMUX Pipeline

Анализ пользовательского опыта на основе UMUX-Lite данных


## Описание
Сервис для обработки, валидации и визуализации данных опросников UMUX-Lite. Принимает CSV-файлы с ответами, считает UMUX-скор, агрегирует результаты по продуктам и версиям, формирует отчеты и дашборды.


## Технологии
Python 3.12+
FastAPI — REST API
Pandas — обработка данных
SQLAlchemy + aiosqlite — асинхронная работа с БД
Plotly — визуализация
Pytest — тестирование

## Установка

```bash

git clone https://github.com/ArOb-1/um_ux_pipeline.git

cd umux-pipeline

python -m venv venv

source venv/bin/activate  # Linux/Mac

venv\Scripts\activate   # Windows


pip install -r requirements.txt
```

## Запуск API сервера

```bash

python run.py

После запуска:

API: http://localhost:8000

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

``` 

## CLI

```bash

python cli.py data/test_data.csv

python cli.py data/test_data.csv

python cli.py --show

python cli.py --clear

```

## API Эндпоинты

| Метод	Эндпоинт |	Описание |
|--------------- | --------- |
| POST	/api/v1/upload |	Загрузка CSV файла |
| GET	/api/v1/results |	Получение результатов |
| GET	/api/v1/products |	Список продуктов |
| GET	/api/v1/dashboard	| HTML дашборд |
| DELETE	/api/v1/clear	| Очистка данных |


## Пример запроса

```bash

curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "files=@data/test_data.csv"

curl "http://localhost:8000/api/v1/results"

curl "http://localhost:8000/api/v1/results?product=Product%20A"
```

## Тесты

Чтобы запустить тесты просто введите из корневой директории:

pytest


## Формат входных данных

CSV файл должен содержать следующие колонки:

| Колонка |	Описание |
| ------- | -------- |
|response_id	 |   Уникальный идентификатор анкеты |
|submitted_at |	Дата и время ответа |
|product	   |    Название продукта |
|product_version |	Версия продукта |
|platform	  |  Платформа (Web/Android/iOS)|
|country	  |      Страна |
|user_segment	| Сегмент пользователя |
|score1, score2	| Ответы UMUX-Lite (1-5) |


Скрипт проверяет и очищает данные:

**Дедупликация**— удаление дубликатов по response_id

**Обязательные поля** — проверка наличия всех полей

**Диапазон скора** — score1 и score2 должны быть в диапазоне 1-5

**Платформа** — только Web/Android/iOS

**Дата** — валидный формат и разумный диапазон (2020-2026)


## Расчет UMUX

**Формула:** $((score1 + score2) / 10) * 100$


## Категории:

Excellent — $≥ 80$

Good — $70-79$

Acceptable — $60-69$

Poor — $< 60$


## Результаты

После обработки создаются:

results/report.md — Markdown отчет со статистикой

results/dashboard.html — Интерактивный дашборд с графиками

results/umux.db — SQLite база данных


## Пример дашборда

Дашборд содержит 4 графика:

Средний UMUX по продуктам — сравнение продуктов

Динамика по месяцам — тренды во времени

Сравнение по платформам — Web vs Android vs iOS

Распределение оценок — гистограмма и box-plot

## Postman

В репозитории есть коллекция для тестирования API:

Импортируйте postman_collection.json

Результаты на тестовых данных

```text

Валидных записей: 1121

Отбраковано: 439

Средний UMUX: 67.78
```
