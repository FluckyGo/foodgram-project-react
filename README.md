# **_Foodgram_**
Foodgram - это "Продуктовый помощник" - онлайн-сервис и соответствующее API. Этот сервис позволяет пользователям делиться своими рецептами, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в закладки и загружать объединенный список ингредиентов, необходимых для приготовления выбранных блюд, перед походом в магазин.

**Ссылка на Фудграм: https://foodgramforpeoples.sytes.net**

**_Репозиторий проекта:_**
```
git@github.com:FluckyGo/foodgram-project-react.git
```

### После каждого push в ветку main будет происходить:

- Проверка на соблюдение стандарта PEP8 с использованием инструментов flake8 и Isort для проверки кода.
- Развертывание проекта на удаленном сервере.
- Уведомление в Telegram в случае успешного выполнения задачи.
    

**_Для использования GitHub Actions необходимо добавить переменные окружения в секции Secrets / Actions в настройках репозитория:_**
```
SECRET_KEY              - секретный ключ Django проекта
DOCKER_PASSWORD         - пароль от Docker Hub
DOCKER_USERNAME         - логин Docker Hub
HOST                    - публичный IP сервера
USER                    - имя пользователя на сервере
PASSPHRASE              - *если ssh-ключ защищен паролем
SSH_KEY                 - приватный ssh-ключ
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, посылающего сообщение

DB_ENGINE               - django.db.backends.postgresql
DB_NAME                 - postgres
POSTGRES_USER           - postgres
POSTGRES_PASSWORD       - postgres
DB_HOST                 - db
DB_PORT                 - 5432 (порт по умолчанию)
```


### _Запуск проекта локально:_

**_Репозиторий проекта, клонируйте на локальный компьютер_**
```
git@github.com:FluckyGo/foodgram-project-react.git
```

**_В директории проекта на примере .env.example создать .env и переместить в папку Infra или создать файл сразу в ней:_**
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
**_Перейти в папку Infra_**
```
cd infra/
```

**_Запустить проект с помощью Docker_**
```
sudo docker compose up --build

sudo docker compose exec backend python manage.py makemigrations

sudo docker compose exec backend python manage.py migrate

sudo docker compose exec backend python manage.py collectstatic

sudo docker compose -f docker-compose.production.yml exec backend cp -r /app//backend_static/static/. /backend_static/static/

sudo docker compose exec backend python manage.py loaddata ingredients.json

sudo docker compose exec backend python manage.py createsuperuser

```

**_Проект доступен локально по адресу : http://localhost:8000/_**


### _Деплой проекта на сервере:_

**_Подключитесь к вашему удалённому серверу:_**
```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
```
**_Подготовьте свой удаленный сервер к публикации проекта:_**
```
sudo npm cache clean --force

sudo apt clean

sudo journalctl --vacuum-time=1d

sudo docker system prune -af
```

**_Установка Docker и Docker Compose на сервер:_**
```
sudo apt update - Обновите пакеты

sudo apt install curl - Консольная утилита, которая умеет скачивать файлы по команде пользователя

curl -fSL https://get.docker.com -o get-docker.sh - скрипт для установки докера с официального сайта 

sudo sh ./get-docker.sh - Скрипт установит Docker

sudo apt install docker-compose-plugin - Скрипт установит Docker Compose

sudo systemctl status docker - Проверка статуса Docker

```
**_Создать папку Foodgram на сервере:_**
```
mkdir foodgram && cd foodgram/
```

**_Создать .env в папке Foodgram на сервере:_**
```
touch .env
```

**_Копировать файлы из 'infra/' на локальном компьютере на сервер:_**
```
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/foodgram/docker-compose.production.yml 
```
**_Запустите Docker Compose с этой конфигурацией на своём компьютере:_**
```
sudo docker compose -f docker-compose.production.yml up
```

 

### *Бэк написал:*
[FluckyGo](https://github.com/FluckyGo)
