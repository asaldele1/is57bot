# Быстрый старт IS57 Telegram Bot

## 1. Получение Telegram Bot Token

1. Перейдите к @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

## 2. Получение User ID

1. Перейдите к @userinfobot в Telegram
2. Получите ваш User ID

## 3. Настройка бота

```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

Вставьте в .env:

```
BOT_TOKEN=ваш_токен_от_BotFather
ADMIN_USER_ID=ваш_user_id
```

## 4. Запуск

```bash
# Простой запуск (автоматически создаст виртуальное окружение)
./start.sh

# Или вручную:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 5. Первоначальная настройка

После запуска отправьте боту:

1. `/start` - Проверить работу
2. `/set_token ваш_api_токен_is57` - Установить API токен
3. `/add_user user_id` - Добавить пользователей
4. В группах: `/add_group` - Разрешить использование в группе

## 6. Основные команды

- `/teams` - Список команд
- `/tasks` - Список заданий
- `/results` - Результаты
- `/help` - Полная справка

## Готово! 🎉

Бот готов к использованию. Полная документация в README.md
