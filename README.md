# 01-sber-stock-data-science
Data Science project: analysis and prediction of SBER stock price movement using MOEX ISS API, time series analysis and machine learning
#  Анализ динамики акций Сбера и прогноз направления движения цены

## О проекте

Data Science проект по анализу исторических данных акций ПАО «Сбербанк».

Цель проекта:
- исследовать динамику стоимости акций;
- выявить закономерности движения цены;
- создать признаки для машинного обучения;
- построить модель прогнозирования направления движения цены.

## Источник данных

MOEX ISS API

Инструмент:
- Тикер: SBER
- Биржа: Московская биржа

## Стек технологий

- Python 3.12
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter Notebook

## Структура проекта
data/
raw/
processed/

notebooks/
01_sber_stock_analysis.ipynb

src/
data_loader.py
features.py
model.py
visualization.py

## Этапы проекта

1. Получение данных MOEX
2. Очистка и подготовка данных
3. Exploratory Data Analysis
4. Создание признаков
5. Обучение ML-модели
6. Оценка качества модели
