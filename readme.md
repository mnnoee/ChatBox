# Simple Chat Application (v0.1)

Простое веб-приложение чата на Flask с аутентификацией пользователей.

## Структура проекта

```
└── ver0.1
    ├── __init__.py
    ├── app.py              # Основное приложение Flask
    ├── backup              # Папка для бэкапов БД
    ├── chat.service        # Systemd service файл
    ├── domain.conf         # Конфигурация Nginx
    └── templates
        ├── chat.html       # Шаблон чата
        └── login.html      # Шаблон авторизации
```

## Установка и настройка

### 1. Зависимости

Установите необходимые пакеты:
```
sudo apt install python3-pip python3-venv nginx sqlite3
sudo pip3 install flask gunicorn werkzeug
```

### 2. Развертывание приложения

1. Создайте необходимые директории:
```
sudo mkdir -p /var/lib/chat_app /var/log/chat_app /var/www/domain/static
sudo chown -R www-data:www-data /var/lib/chat_app /var/log/chat_app
sudo chmod 750 /var/lib/chat_app
```

2. Скопируйте файлы проекта:
```
sudo cp -r ver0.1/* /var/lib/chat_app/
sudo chown -R www-data:www-data /var/lib/chat_app
```

3. Инициализируйте БД из под юзера www-data:
```
cd /var/lib/chat_app
python3 app.py
```



### 3. Настройка Systemd Service

1. Скопируйте файл сервиса:
```
sudo cp /var/lib/chat_app/chat.service /etc/systemd/system/
```

2. Запустите сервис:
```
sudo systemctl daemon-reload
sudo systemctl enable chat.service
sudo systemctl start chat.service
```

### 4. Настройка Nginx

1. Скопируйте конфигурацию:
```
sudo cp /var/lib/chat_app/domain.conf /etc/nginx/sites-available/domain
sudo ln -s /etc/nginx/sites-available/domain /etc/nginx/sites-enabled/
```

2. Проверьте и перезапустите Nginx:
```
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Настройка SSL (опционально)

Для HTTPS рекомендуется использовать Let's Encrypt:
```
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d domain -d www.domain
```

## Бэкапы базы данных

Автоматическое резервное копирование настроено через cron:
```
0 3 * * * /usr/bin/sqlite3 /var/lib/chat_app/chat.db ".backup /var/lib/chat_app/backup/chat-$(date +\%Y\%m\%d).db"
```

Для ручного бэкапа:
```
sqlite3 /var/lib/chat_app/chat.db ".backup /var/lib/chat_app/backup/chat-manual.db"
```

## Особенности приложения

- Регистрация и аутентификация пользователей
- Хранение сообщений в SQLite базе данных
- Хеширование паролей с помощью Werkzeug
- Защита от CSRF через Flask сессии
- Логирование через Gunicorn и Nginx

## Логи

Основные логи находятся в:
- `/var/log/chat_app/access.log` - доступ к приложению
- `/var/log/chat_app/error.log` - ошибки приложения
- `/var/log/nginx/domain.access.log` - доступ через Nginx
- `/var/log/nginx/domain.error.log` - ошибки Nginx

## Управление сервисом

`sudo systemctl restart chat.service` - Перезапуск приложения

`sudo systemctl status chat.service` - Проверка статуса

`journalctl -u chat.service -f` -Просмотр логов


Замените все вхождения `domain.` на ваш реальный домен при настройке.
А так же

`app.secret_key='Rdjzan0sUsSP7KfPoheB'` - Замените ключ на свой в файле [app.py](app.py)

Проект крафтился чисто между тикетами в тпх
