import datetime
import os
from dotenv import load_dotenv

from aiogram import Bot, types
from aiogram.utils import executor
import asyncio
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

import buttons
import key
import store
import buttons
from store import user_reminder_data
from db.data import ReminderDatabase
import data_with_freq
import func_for_date
import json_date

load_dotenv()
token = os.getenv('TOKEN')

storage = MemoryStorage()
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
data_base = ReminderDatabase()



# Handle /start command
@dp.message_handler(Command('start'), state=None)
async def welcome(message):
    data_base.add_user(message.chat.id)
    data_base.add_reminder_frequency(data_with_freq.frequencies)

    await bot.send_message(message.chat.id, f'Привет, "{message.from_user.first_name}",'
                                            f' Бот Работает',
                           parse_mode='Markdown',
                           reply_markup=buttons.keyboard)


# ---Обработка добавления упоминания---
# Handle button "Добавить напоминание"
@dp.message_handler(lambda message: message.text == "Добавить напоминание")
async def add_reminder_start(message: types.Message):
    await message.answer("Введите заголовок упоминания:")
    # Set the current user ID as the key for reminder data
    user_reminder_data[message.from_user.id] = {"title": None,
                                                "description": None,
                                                "date": None,
                                                "time": None,
                                                "frequency_index": None
                                                }


@dp.message_handler(
    lambda message: user_reminder_data.get(message.from_user.id) and not user_reminder_data[message.from_user.id][
        "title"])
async def add_reminder_title(message: types.Message):
    # Store the title in the reminder data
    user_reminder_data[message.from_user.id]["title"] = message.text
    await message.answer("Введите описание упоминания:")


@dp.message_handler(
    lambda message: user_reminder_data.get(message.from_user.id) and not user_reminder_data[message.from_user.id][
        "description"])
async def add_reminder_description(message: types.Message):
    # Store the description in the reminder data
    user_reminder_data[message.from_user.id]["description"] = message.text
    store.option = 'add_reminder'
    await bot.send_message(message.chat.id,
                           text=f'Выберите дату: ',
                           reply_markup=buttons.date_button()[-1],
                           parse_mode='Markdown')


# @dp.message_handler(
#     lambda message: user_reminder_data.get(message.from_user.id) and not user_reminder_data[message.from_user.id][
#         "date"])
# async def add_reminder_date(message: types.Message):
#     # try:
#     #     # Parse the date from the user input
#     #     reminder_date = datetime.datetime.strptime(message.text, "%d.%m.%Y").date()
#     # except ValueError:
#     #     await message.answer("Некорректный формат даты. Попробуйте снова.")
#     #     return
#     reminder_date = datetime.datetime.strptime(message.text, "%d.%m.%Y").date()
#     # Store the date in the reminder data
#     user_reminder_data[message.from_user.id]["date"] = reminder_date
#     await message.answer("Выберите частоту упоминания:",
#                          reply_markup=buttons.keyboard_freq(data_base.get_reminder_frequency()))


# @dp.message_handler(
#     lambda message: user_reminder_data.get(message.from_user.id) and not user_reminder_data[message.from_user.id][
#         "frequency_index"])
# async def add_reminder_freq(message: types.Message):
#     # Print reminder frequency options
#     await message.answer("Выберите частоту упоминания:",
#                          reply_markup=buttons.keyboard_freq(data_base.get_reminder_frequency()))


@dp.callback_query_handler(lambda query: query.data.startswith("frequency_"))
async def process_frequency_callback(callback_query: types.CallbackQuery):
    frequency_index = int(callback_query.data.split("_")[1])
    # Store the frequency index in the reminder data
    user_id = callback_query.from_user.id
    user_reminder_data[user_id]["frequency_index"] = frequency_index
    pprint()
    if store.option == 'add_reminder':
        pass
    await bot.answer_callback_query(callback_query.id)


def pprint():
    print(store.user_reminder_data)


# ------------------------------

# ---Обработка даты, выбранной из календаря---
@dp.callback_query_handler(text_contains='previous')
async def join(call: types.CallbackQuery):
    date = func_for_date.prev_month()
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                        reply_markup=buttons.date_button(date)[-1])


@dp.callback_query_handler(text_contains='next')
async def join(call: types.CallbackQuery):
    date = func_for_date.next_month()
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                        reply_markup=buttons.date_button(date)[-1])


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("date_"))
async def spend_money(call: types.CallbackQuery):
    answer = int(call.data[5:])
    if store.option == 'add_reminder':
        user_id = call.from_user.id
        user_reminder_data[user_id]["date"] = answer
        await call.message.edit_text("Выберите частоту упоминания:",
                                     reply_markup=buttons.keyboard_freq(data_base.get_reminder_frequency()))


# ------------------------------

# Handle button "Удалить напоминание"
@dp.message_handler(lambda message: message.text == "Удалить напоминание")
async def remove_reminder(message: types.Message):
    # Your logic for removing a reminder goes here
    await message.answer("Функция 'Удалить напоминание' пока не реализована.")


# Handle button "Просмотреть все упоминания"
@dp.message_handler(lambda message: message.text == "Просмотреть все упоминания")
async def view_reminders(message: types.Message):
    # Your logic for viewing all reminders goes here
    await message.answer("Функция 'Просмотреть все упоминания' пока не реализована.")


if __name__ == '__main__':
    print('Good!')
executor.start_polling(dp)
