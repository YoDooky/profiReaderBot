import datetime
import ebooklib
from ebooklib import epub
from config.bot_config import MAX_MESSAGE_LENGHT
from bs4 import BeautifulSoup
from typing import List, Dict

from database.controllers import books_controller
from app_types import Book, Progress
import vars_global


def get_book_name(filepath: str) -> str:
    """Returns table name from filepath"""
    filename = filepath.split('/')[-1]
    table_name = "".join(ch for ch in filename if ch.isalnum())
    table_name = ''.join(i for i in table_name if not i.isdigit())
    return table_name.lower()


def get_parts_amount(book_name: str) -> int:
    data = books_controller.db_read_book_data(book_name)
    return len(data)


def get_last_part_numb(user_id: int, book_name: str) -> int:
    """Returns last red part"""
    try:
        progress = books_controller.db_read_user_progress(user_id, book_name)
        if not progress:
            return 1
        last_red_page = progress.last_part_numb
    except TypeError:
        last_red_page = 1
    return last_red_page


def init_first_book(user_id: int, filepath: str) -> str | Dict:
    """Writes progress and returns books part text from first loaded book"""
    write_book_to_db(user_id, filepath)
    book_name = get_book_name(filepath)
    new_book_flag = True
    last_red_page = get_last_part_numb(user_id, book_name)
    pages_amount = get_parts_amount(book_name)
    if last_red_page > 1:
        new_book_flag = False
    books_part_text = books_controller.db_read_books_part_text(book_name, last_red_page)
    progress_data = Progress(telegram_id=user_id,
                             last_part_numb=last_red_page,
                             parts_amount=pages_amount,
                             book_name=book_name,
                             read_timestamp=str(datetime.datetime.now()),
                             shedule_read_timestamp=str(datetime.datetime.now() + datetime.timedelta(days=1)))
    books_controller.db_update_users_table(user_id, book_name)
    books_controller.db_write_progress(progress_data)
    return {'books_part_text': books_part_text, 'new_book': new_book_flag}


def replace_unsupported_symbols(string_object: str) -> str:
    unsupported_symbols = ["<", ">", "&", "'"]
    replace_symbols = ["&lt", "&gt", "&amp", "`"]
    for num, each in enumerate(unsupported_symbols):
        string_object = string_object.replace(unsupported_symbols[num], replace_symbols[num])
    return string_object


def get_toc_hrefs(filepath: str) -> List[str]:
    book = epub.read_epub(filepath)
    books_parts = []

    def inner_func(parts_list, iterator):
        for part in iterator:
            try:
                parts_list.append(part.href.split('#')[0])
            except Exception as ex:
                inner_func(parts_list, part)

    inner_func(books_parts, book.toc)
    return books_parts


def parse_epub_data(filepath: str) -> str:
    """Returns text from epub"""
    toc_hrefs = get_toc_hrefs(filepath)
    book = epub.read_epub(filepath)
    full_text = []
    for ref in toc_hrefs:
        for document in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            if document.file_name != ref:
                continue
            soup = BeautifulSoup(document.content, features='xml')
            paragraph_text = [each.text for each in soup.find_all('p')]
            full_text.append('\n'.join(paragraph_text))
    full_string = '\n'.join(full_text)
    clean_string = replace_unsupported_symbols(full_string)
    return clean_string


def divide_string_to_parts(string_object: str, user_id: int) -> List[Book]:
    """Divivide string to list parts"""
    new_string = string_object.split('. ')
    book_part = ''
    wrap_list = []
    for part in new_string:
        next_element_lenght = len(book_part) + len(part)
        if next_element_lenght >= MAX_MESSAGE_LENGHT:
            wrap_list.append(book_part)
            book_part = ''
        book_part = f'{book_part}{part}. '
    book_parts = []
    for num_part, part in enumerate(wrap_list):
        # book_parts.append({'user_create_id': user_id, 'part_numb': num_part + 1, 'part_text': part})
        book_parts.append(Book(user_create_id=user_id, part_numb=num_part + 1, part_text=part))
    return book_parts


def get_target_part_text(user_id: int, dec_inc: str) -> str | None:
    book_filename = books_controller.db_read_user_current_book(user_id)
    progress = books_controller.db_read_user_progress(user_id, book_filename)
    if progress.last_part_numb == progress.parts_amount:
        return
    if dec_inc == 'dec':
        target_page = progress.last_part_numb - 1
    else:
        target_page = progress.last_part_numb + 1
    books_part_text = books_controller.db_read_books_part_text(progress.book_name, target_page)
    progress.last_part_numb = target_page
    progress.read_timestamp = str(datetime.datetime.now())
    progress.shedule_read_timestamp = str(datetime.datetime.now() + datetime.timedelta(days=1))
    books_controller.db_update_progress_table(progress)
    vars_global.update_schedule = [True, user_id]
    return books_part_text


def write_book_to_db(user_id: int, filepath: str):
    """Writes book text to DB"""
    epub_text = parse_epub_data(filepath)
    text_parts = divide_string_to_parts(epub_text, user_id)
    table_name = get_book_name(filepath)
    books_controller.db_add_book_table(table_name, text_parts)


def get_progress_data(user_id: int, book_name: str):
    progress_data = books_controller.db_read_user_progress(user_id, book_name)
    last_part_numb = progress_data.last_part_numb
    parts_amount = progress_data.parts_amount
    progress_percent = round(last_part_numb * 100 / parts_amount, 2)
    return {
        'last_part_numb': last_part_numb,
        'parts_amount': parts_amount,
        'progress_percent': progress_percent
    }


def format_schedule_time(user_progress: Progress) -> str:
    """Format time to HH:MM format"""
    raw_scheduled_time = user_progress.shedule_read_timestamp
    scheduled_time = raw_scheduled_time.split(' ')[1].split('.')[0].split(':')
    scheduled_time = ':'.join([scheduled_time[0], scheduled_time[1]])
    return scheduled_time
