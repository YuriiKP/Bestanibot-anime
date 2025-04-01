import os

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

from loader import dp, bot, am, um
from texts import quotes_by_type



@dp.message(F.text == quotes_by_type)
async def message_with_type_quotes(message: Message, state: FSMContext):
    await state.clear()
    
    message_with_type_quotes = InlineKeyboardMarkup(
        inline_keyboard= [
            [InlineKeyboardButton(text='😄 Радость', switch_inline_query_current_chat='/радость'), InlineKeyboardButton(text='😘 Хвалить', switch_inline_query_current_chat='/хвалить'),],
            [InlineKeyboardButton(text='😔 Грусть', switch_inline_query_current_chat='/грусть'), InlineKeyboardButton(text='🤯 Ругать', switch_inline_query_current_chat='/ругать'),],
            [InlineKeyboardButton(text='😍 Любовь', switch_inline_query_current_chat='/любовь'), InlineKeyboardButton(text='😡 Злость', switch_inline_query_current_chat='/злость'),],
            [InlineKeyboardButton(text='🥺 Прощание', switch_inline_query_current_chat='/прощание'), InlineKeyboardButton(text=' 😉 Согласие', switch_inline_query_current_chat='/согласие'),],
            [InlineKeyboardButton(text='🤗 Приветствие', switch_inline_query_current_chat='/приветствие'), InlineKeyboardButton(text='🫣 Отрицание', switch_inline_query_current_chat='/отрицание'),],
        ]
    )

    await message.answer(
        text='Выберите какой тип цитат хотите найти 👇\nИли введите команду /rand чтобы получить рандомную фразу',
        reply_markup=message_with_type_quotes
    )