from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from texts import *


class MyCallback(CallbackData, prefix='back'):
    step: str
    action: str

select_type_quote = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='😄 Радость', callback_data=MyCallback(step='радость', action='type').pack()), InlineKeyboardButton(text='😘 Хвалить', callback_data=MyCallback(step='хвалить', action='type').pack()),],
        [InlineKeyboardButton(text='😔 Грусть', callback_data=MyCallback(step='грусть', action='type').pack()), InlineKeyboardButton(text='🤯 Ругать', callback_data=MyCallback(step='ругать', action='type').pack()),],
        [InlineKeyboardButton(text='😍 Любовь', callback_data=MyCallback(step='любовь', action='type').pack()), InlineKeyboardButton(text='😡 Злость', callback_data=MyCallback(step='злость', action='type').pack()),],
        [InlineKeyboardButton(text='🥺 Прощание', callback_data=MyCallback(step='прощание', action='type').pack()), InlineKeyboardButton(text=' 😉 Согласие', callback_data=MyCallback(step='согласие', action='type').pack()),],
        [InlineKeyboardButton(text='🤗 Приветствие', callback_data=MyCallback(step='приветствие', action='type').pack()), InlineKeyboardButton(text='🫣 Отрицание', callback_data=MyCallback(step='отрицание', action='type').pack()),],
        [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_time_code', action='back').pack())]
    ]
)


main_admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=add_quote_text), KeyboardButton(text=quotes_by_type)],
        [KeyboardButton(text=user_profile), KeyboardButton(text=about_users_bot)],
        [KeyboardButton(text=qoutes_moder), KeyboardButton(text=add_admin), KeyboardButton(text=edit_qoute_button)],
        [KeyboardButton(text=detect_anime_button),],
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=add_quote_text), KeyboardButton(text=quotes_by_type)],
        [KeyboardButton(text=user_profile), KeyboardButton(text=qoutes_moder), KeyboardButton(text=edit_qoute_button)],
        [KeyboardButton(text=detect_anime_button),],
    ],
    resize_keyboard=True
)

moder_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=add_quote_text), KeyboardButton(text=quotes_by_type)],
        [KeyboardButton(text=user_profile), KeyboardButton(text=qoutes_moder)],
        [KeyboardButton(text=detect_anime_button),],
    ],
    resize_keyboard=True
)

user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=quotes_by_type), KeyboardButton(text=user_profile)],
        [KeyboardButton(text=detect_anime_button), KeyboardButton(text=add_quote_text),],
    ],
    resize_keyboard=True
)

pidor_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=quotes_by_type), KeyboardButton(text=user_profile)],
    ],
    resize_keyboard=True
)