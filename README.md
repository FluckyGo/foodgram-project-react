# **_Foodgram_**
Foodgram - это "Продуктовый помощник" - онлайн-сервис и соответствующее API. Этот сервис позволяет пользователям делиться своими рецептами, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в закладки и загружать объединенный список ингредиентов, необходимых для приготовления выбранных блюд, перед походом в магазин.

**_Ссылка на [Фудграм](foodgramforpeoples.sytes.net "Гиперссылка к проекту.")_**

**_Репозиторий проекта:_**
```
git@github.com:FluckyGo/foodgram-project-react.git
```

### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

**_Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:_**
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

**_Создать папку Foodgram на сервере:_**
```
mkdir foodgram && cd foodgram/
```

**_Создать папку .env на сервере:_**
```
touch .env
```

**_Копировать файлы из 'infra/' на локальном компьютере на сервер:_**
```
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/foodgram/docker-compose.production.yml 
```

**_Запуск контейнера:_**
```
sudo docker-compose up -d
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

sudo docker compose exec backend python manage.py migrate

sudo docker compose exec backend python manage.py collectstatic

sudo docker compose exec backend python manage.py loaddata ingredients.json

sudo docker compose exec backend python manage.py createsuperuser

```

**_Проект доступен локально по адресу : http://localhost/_**

**_Cпецификация API по адресу : http://localhost/api/docs/_**


### _Деплой проекта на сервере:_

**_Подключитесь к вашему удалённому серверу:_**
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера

**_Установка Docker и Docker Compose на сервер:_**
```
sudo apt update - Обновите пакеты

sudo apt install curl - Консольная утилита, которая умеет скачивать файлы по команде пользователя

curl -fSL https://get.docker.com -o get-docker.sh - скрипт для установки докера с официального сайта 

sudo sh ./get-docker.sh - Скрипт установит Docker

sudo apt install docker-compose-plugin - Скрипт установит Docker Compose

sudo systemctl status docker - Проверка статуса Docker

```


### _Бэк написал_:
**(https://github.com/FluckyGo)**