from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import datetime
from calendar import monthrange
import json_date

# ---Начальные кнопки (кнопки выбора действия)---
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить напоминание"),
            KeyboardButton(text="Удалить напоминание"),
        ],
        [
            KeyboardButton(text="Просмотреть все упоминания"),
        ],
    ],
    resize_keyboard=True
)


# ------------------------------------

# ---Кнопки для выбора frequency---
def keyboard_freq(frequencies):
    keyboard_freq = InlineKeyboardMarkup()
    for frequency, index in frequencies:
        callback_data = f"frequency_{index}"
        keyboard_freq.add(InlineKeyboardButton(text=frequency, callback_data=callback_data))
    return keyboard_freq


# ------------------------------------

# ---Кнопки для выбора frequency---
def empty_button():
    return InlineKeyboardButton('   ', callback_data='pass')


def date_button(date=datetime.datetime.now()):
    json_date.create_json()
    str_date = date.strftime('%Y.%m')
    date_button = InlineKeyboardMarkup(row_width=7)
    date_button.row(InlineKeyboardButton(f'<--', callback_data='previous'),
                    InlineKeyboardButton(f'{str_date}', callback_data='pass'),
                    InlineKeyboardButton(f'-->', callback_data='next'))
    date_button.row(InlineKeyboardButton(f'Mo', callback_data='pass'),
                    InlineKeyboardButton(f'Tu', callback_data='pass'),
                    InlineKeyboardButton(f'We', callback_data='pass'),
                    InlineKeyboardButton(f'Th', callback_data='pass'),
                    InlineKeyboardButton(f'Fr', callback_data='pass'),
                    InlineKeyboardButton(f'Sa', callback_data='pass'),
                    InlineKeyboardButton(f'Su', callback_data='pass'))
    sp = []
    count = 0
    week_count = monthrange(date.year, date.month)
    first_weekday = week_count[0]  # первый день недели месяца
    count_days = week_count[1]  # кол-во дней в месяце
    count_d = 0
    start_empty_button = True

    while True:
        if start_empty_button:
            for i in range(first_weekday):
                sp.append(empty_button())
                count += 1
            days_left = 7 - count
            for i in range(1, days_left + 1):
                count_d += 1
                sp.append(InlineKeyboardButton(f'{i}', callback_data=f'date_{i}'))
            date_button.row(*sp)
            sp = []
            count = 0
            start_empty_button = False
        elif count_d < count_days:
            count_d += 1
            count += 1
            sp.append(InlineKeyboardButton(f'{count_d}', callback_data=f'date_{count_d}'))
            if count == 7:
                date_button.row(*sp)
                sp = []
                count = 0

        elif count_d >= count_days:
            count += 1
            sp.append(empty_button())
            if count == 7:
                date_button.row(*sp)
                break

    return date, date_button
# ------------------------------------
