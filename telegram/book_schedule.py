import aiogram.utils.exceptions
from aiogram import Bot
import aioschedule
import asyncio

from database.controllers import books_controller
import vars_global
from telegram import markups
from app_types import User
from telegram import aux_funcs


class Schedule:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_book_text(self, user_id: int, user_obj: User):
        """Send book text by shedule"""
        book_name = user_obj.current_book
        user_progress = books_controller.db_read_user_progress(user_id, book_name)
        if user_progress.last_part_numb >= user_progress.parts_amount:
            aioschedule.clear(f'{user_id}')
            return
        next_book_part = user_progress.last_part_numb + 1
        books_part_text = books_controller.db_read_books_part_text(book_name, next_book_part)
        user_progress.last_part_numb = next_book_part
        books_controller.db_update_progress_table(user_progress)
        keyboard = markups.get_nav_menu(user_id)
        try:
            await self.bot.send_message(chat_id=user_id, text=books_part_text, reply_markup=keyboard)
        except aiogram.utils.exceptions.BotBlocked:
            aioschedule.clear(f'{user_id}')
            books_controller.db_update_users_table(user_id, '')
            return

    async def scheduler(self):
        """Shedule loop"""
        self.startup_schedule()  # init schedule
        while True:
            if vars_global.update_schedule[0]:
                self.update_schedule()
                vars_global.update_schedule[0] = False
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    def startup_schedule(self):
        """Make shedule via DB"""
        print('[SHEDULE] Starting up schedule...')
        aioschedule.clear()
        user_data = books_controller.db_read_users_data()
        for user in user_data:
            user_id = user.telegram_id
            user_book = user.current_book
            user_progress = books_controller.db_read_user_progress(user_id, user_book)
            if not user_progress:
                continue
            if user_progress.last_part_numb >= user_progress.parts_amount:
                adawda
                continue
            if not user_book:
                continue
            schedule_time = aux_funcs.format_schedule_time(user_progress)
            aioschedule.every().day.at(schedule_time).do(self.send_book_text,
                                                         user_id=user_id,
                                                         user_obj=user).tag(f'{user_id}')

    def update_schedule(self):
        print('[SHEDULE] Updating user schedule...')
        current_id = vars_global.update_schedule[1]
        aioschedule.clear(f'{current_id}')
        user_data = books_controller.db_read_users_data()
        for user in user_data:
            if user.telegram_id != current_id:
                continue
            user_id = user.telegram_id
            user_book = user.current_book
            user_progress = books_controller.db_read_user_progress(user_id, user_book)
            if not user_progress:
                continue
            if user_progress.last_part_numb >= user_progress.parts_amount:
                continue
            if not user_book:
                continue
            schedule_time = aux_funcs.format_schedule_time(user_progress)
            aioschedule.every().day.at(schedule_time).do(self.send_book_text,
                                                         user_id=user_id,
                                                         user_obj=user).tag(f'{user_id}')
