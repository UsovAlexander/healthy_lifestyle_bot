### Telegram-бот для отслеживания нормы воды, калорий и физической активности с использованием aiogram 3.x.

## Основной функционал
- Профиль пользователя: Настройка веса, роста, возраста, уровня активности и города

- Расчет норм: Автоматический расчет дневных норм воды и калорий

- Трекинг: Логирование воды, еды и тренировок

- Прогресс: Отслеживание прогресса с графиками и статистикой

## Архитектура проекта
```
.
├── Dockerfile
├── README.md
├── config.py
├── database.py
├── handlers
│   ├── __init__.py
│   ├── profile.py
│   ├── progress.py
│   └── tracking.py
├── healthy_lifestyle_bot.db
├── main.py
├── middleware
│   └── logging_middleware.py
├── requirements.txt
└── services
    ├── __init__.py
    ├── calculations.py
    ├── chart.py
    ├── food.py
    ├── recommendations.py
    └── weather.py
```

## Деплой

Склонируйте репозиторий
```
git clone https://github.com/UsovAlexander/healthy_lifestyle_bot.git
```
Установите виртуальное окружение и все зависимости
```
pip install -r requirements.txt
```
Создайте файл .env с переменными окружения
```
BOT_TOKEN=ваш_токен_бота_здесь
WEATHER_API_KEY=ваш_api_ключ_погоды_здесь
```
Для создания образа
```
docker build -t healthy-lifestyle-bot . 
```
Для запуска, остановки и удаления контейнера
```
docker run -d --name hl-bot --env-file .env healthy-lifestyle-bot
docker stop hl-bot 
docker rm -f hl-bot 
```
Для просмотра логов
```
docker logs hl-bot -f 
```