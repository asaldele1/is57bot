#!/bin/bash

# Скрипт для запуска IS57 Telegram Bot

echo "Запуск IS57 Telegram Bot..."

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден. Установите Python 3.7+ для работы бота."
    exit 1
fi

# Проверка наличия pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "Ошибка: pip не найден. Установите pip для установки зависимостей."
    exit 1
fi

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo "Предупреждение: Файл .env не найден!"
    echo "Создайте файл .env на основе .env.example и заполните необходимые переменные."
    echo "Скопируйте .env.example в .env:"
    echo "cp .env.example .env"
    echo "Затем отредактируйте .env файл."
    exit 1
fi

# Запуск бота
echo "Запуск бота..."
python main.py