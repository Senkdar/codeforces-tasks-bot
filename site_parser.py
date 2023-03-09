from dotenv import load_dotenv
import logging
import os
import psycopg2
import time
from bs4 import BeautifulSoup
import requests


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
RETRY_TIME = 3600


def create__task_table():
    """Создание таблицы в базе данных."""
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks(
        number TEXT,
        name TEXT,
        category TEXT[],
        difficulty INTEGER,
        resolved TEXT,
        link TEXT
    );
    ''')


def parse_page(url: str) -> None:
    """Функция для парсинга страницы и добавления задач в БД.
        Если задача существует, то обновляем количество решивших.
    """
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    tasks = soup.find_all('tr')
    c = 0

    for task in tasks:
        if task.find('td') is None:
            continue
        raw_data = task.get_text(strip=True, separator='|')
        data = raw_data.split('|')
        print(data)
        task_id = data.pop(0)
        task_name = data.pop(0)
        task_resolved = data.pop(-1)
        # не у всех задач есть сложность
        # если её нет - пропускаем задачу
        try:
            task_difficulty = int(data.pop(-1))
        except BaseException:
            continue
        if len(data) > 1:
            data.remove(',')
        task_category = data
        link = 'https://codeforces.com/' + task.find('a').get('href')
        print(task_category)

        cur.execute('''SELECT *
                    FROM tasks
                    WHERE name=%s;''',
                    (task_name,))
        result = cur.fetchall()
        if not result:
            cur.execute('''INSERT INTO tasks
                        VALUES(%s, %s, %s, %s, %s, %s);''',
                        (task_id, task_name, task_category,
                            task_difficulty, task_resolved, link))
        else:
            cur.execute(
                'UPDATE tasks SET resolved=%s'
                'WHERE name=%s;',
                (task_resolved, task_name)
            )
        connection.commit()
        c+=1
        if c>4:
            break


def parse_all_pages() -> None:
    """Функция для парсинга всех страниц"""
    for i in range(1, 15):
        # по умолчанию, страниц меньше, чем на Codeforces
        url = f'https://codeforces.com/problemset/page/{i}?order=BY_SOLVED_DESC'
        parse_page(url)
        logging.info(f'Получили данные со страницы {i}')


if __name__ == '__main__':

    try:
        connection = psycopg2.connect(
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            host=os.getenv('HOST'),
            port=os.getenv('PORT')
        )
        cur = connection.cursor()
        logging.info('Успешное подключение к базе данных')
    except (Exception, psycopg2.Error) as error:
        logging.error('Ошибка при подключении к PostgreSQL', error)

    create__task_table()
    # while True:
    #     parse_all_pages()
    #     logging.info('Остановка программы на 1 час')
    #     time.sleep(RETRY_TIME)
    parse_page('https://codeforces.com/problemset/page/1?order=BY_SOLVED_DESC')