from datetime import datetime
import os

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

from loader import dp, bot, am, um
from texts import user_profile


@dp.message(F.text == user_profile)
async def show_user_profile(message: Message, state: FSMContext):
    await state.clear()

    user = await um.get_user(message.from_user.id)
    reg_time: datetime = datetime.fromisoformat(user[5])

    text = f'<b>🆔 ID</b>\n{message.from_user.id}\n<b>📆 ДАТА РЕГИСТРАЦИИ</b>\n{reg_time.date()} {reg_time.hour}-{reg_time.minute}\n'
    text += f'<b>🌐 КОЛ-ВО ЦИТАТ</b>\n{user[4]}'

    await message.answer(
        text=text
    )