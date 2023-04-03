# Codeforces tasks bot
Телеграм бот, который автоматически подбирает и отправляет пользователю подборку из 10 задач на основе заданных параметров сложности и темы. Для получения задач бот парсит данные с сайта Codforces.com


## Как запустить проект:
1. Клонировать репозиторий и перейти в него в командной строке:

```bash
  git clone https://github.com/Senkdar/codeforces-tasks-bot
  
  cd codeforces-tasks-bot
```
2. Создать файл .env в папке backend с настройками:
 ```
SECRET_KEY=<КЛЮЧ>
TOKEN = <Ваш токен>
DB_NAME=<ИМЯ БАЗЫ ДАННЫХ>
DB_USER=<ИМЯ ПОЛЬЗОВАТЕЛЯ>
DB_PASSWORD=<ПАРОЛЬ>
DB_HOST=db
DB_PORT=5432
```
3. Выполнить команду:
```
docker-compose up -d
```
