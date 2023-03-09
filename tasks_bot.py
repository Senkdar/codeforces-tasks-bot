from dotenv import load_dotenv
import logging
import os
import psycopg2
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Filters,
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler
)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
TOKEN = os.getenv('TOKEN')

category_button = {
    'Математика': 'math',
    'Перебор': 'brute force',
    'Cтроки': 'strings',
    'Реализация': 'implementation',
    'Жадные алгоритмы': 'greedy',
    'Бинарный поиск': 'binary search',
    'Конструктивные алгоритмы': 'constructive algorithms',
    'Сортировки': 'sortings',
    'Структуры данных': 'data structures',
}

difficulty_button = {
    '800': 800,
    '900': 900,
    '1000': 1000,
    '1100': 1100,
    '1200': 1200,
    '1300': 1300,
    '1400': 1400,
    '1500': 1500,
    '1600': 1600,
}


def get_tasks_by_category_and_difficulty(category: str, difficulty: int) -> list:
    """Функция для получения задач по категории и сложности."""
    cur.execute("""
        SELECT *
        FROM tasks
        WHERE category=%s AND difficulty=%s
        ORDER BY resolved DESC
        LIMIT 10;""",
                (category, difficulty))
    logging.info(
        f'Получили задачи по выбранным параметрам: {category} {difficulty}'
    )
    tasks = cur.fetchall()
    return tasks


def get_task_by_number(number: str) -> list:
    """Получение задачи по номеру."""
    cur.execute("""
        SELECT *
        FROM tasks
        WHERE number=%s;""",
                (number,))
    result = cur.fetchone()
    return result


def start(update, context):
    """Стартовая функция бота."""
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup(
        [['/newtask']], resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет! этот бот может прислать подборку из 10 задач '
        'по выбранной сложности и категории. '
        'Также, можно ввести номер задачи, например, 1790B (буквы на латинице) '
        'и бот выдаст всю информацию о задаче',
        reply_markup=buttons
    )
    logging.info('Успешная инициализация бота')


def find_task(update, context):
    """Поиск по номеру задачи"""
    chat = update.effective_chat
    number = update.message.text
    data = get_task_by_number(number)
    if data is not None:
        logging.info(f'Получили задачу по указанному номеру: {number}')
        context.bot.send_message(
            chat_id=chat.id,
            text=f'Номер: {data[0]}. '
                 f'Название: {data[1]}. '
                 f'Категория: {data[2]}. '
                 f'Сложность: {data[3]}. '
                 f'Количество решивших: {data[4]}. '
                 f'Ссылка: {data[5]}'
        )
        logging.info('Задача отправлена в чат')
    else:
        context.bot.send_message(
            chat_id=chat.id,
            text='Задачи с таким номером не найдено'
        )
        logging.warning('Задачи с указанным номером не найдено')


def new_task(update, context):
    """Отображение кнопок для выбора темы"""
    keyboard = []
    for button_name in category_button:
        keyboard.append([InlineKeyboardButton(
            button_name, callback_data=f'Тема_{button_name}'
        )])
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Выберите тему:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def get_difficulty(update, _):
    """Отображение кнопок для выбора сложности задачи."""
    keyboard = []
    query = update.callback_query
    category = query.data.split('_')[1]
    logging.info('Успешный выбор категории')
    for button_name in difficulty_button:
        keyboard.append([InlineKeyboardButton(
            button_name, callback_data=f'Выбор_{category}_{button_name}'
            )])
    query.answer(f"Выбранный вариант: {category}")
    query.edit_message_text(
        text='Выберите сложность:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def get_tasks_list(update, context):
    """Получение 10 задач: наименование и ссылка на задачу"""
    query = update.callback_query
    category = query.data.split('_')[1]
    difficulty = query.data.split('_')[2]
    query.answer(f'выбранная сложность:{difficulty}')
    logging.info('Успешный выбор сложности')
    chat = update.effective_chat
    data = [(task[1], task[5]) for task in
            get_tasks_by_category_and_difficulty(
            category_button.get(category),
            difficulty_button.get(difficulty))]
    if len(data) > 0:
        for i in data:
            context.bot.send_message(
                chat_id=chat.id,
                text=i
            )
        logging.info('Успешно отправлена выборка задач')
    else:
        context.bot.send_message(
                chat_id=chat.id,
                text='В базе отсутствуют задачи по выбранным параметрам'
            )
        logging.warning('В базе отсутствуют задачи по выбранным параметрам')


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

    updater = Updater(token=TOKEN)
    handler = updater.dispatcher.add_handler

    handler(CommandHandler('start', start))
    handler(CommandHandler('newtask', new_task))
    handler(MessageHandler(Filters.text, find_task))
    handler(CallbackQueryHandler(get_difficulty, pattern='Тема'))
    handler(CallbackQueryHandler(get_tasks_list, pattern='Выбор'))

    updater.start_polling()
    updater.idle()

    connection.close()