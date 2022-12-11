import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
ADMIN_ID = [int(os.getenv('ADMIN_ID_1')), int(os.getenv('ADMIN_ID_2'))]

WEBHOOK_PATH = f"/main/{TOKEN}"
APP_URL = os.getenv('APP_URL')
WEBHOOK_URL = APP_URL + WEBHOOK_PATH

EPUB_FOLDER = 'C:/PyProject/profiReaderBot/epub_files/'

MAX_MESSAGE_LENGHT = 3500

# bot default messages
GREETING_MSG = '👇 Нажми на кнопку "Начать работу с ботом" для продолжения'
ADD_BOOK_MSG = '👉 Отправь мне книгу в формате ePub'
BOOK_FORMAT_ERR_MSG = '⚠ Проверь формат. Файл должен быть в формате ePub'
FIRST_BOOK_MSG = '👌 Отлично. Держи свою первую страницу. Если захочешь начать другую книгу, введи комманду /select'
SAME_BOOK_MSG = '👌 Отлично. Книга уже была добавлена ранее. Продолжаем чтение...Если захочешь начать другую книгу, введи комманду /select'
REEDING_COMPLETE_MSG = '🥳 Поздравляем! Ты успешно закончил чтение книги. Если захочешь начать другую книгу, введи комманду /select'
