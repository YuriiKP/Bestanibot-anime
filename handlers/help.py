from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from loader import dp
from texts import help_info



# Случайная цитата, в лс или в чате
@dp.message(Command('help'))
async def show_info(message: Message, state: FSMContext):
    await message.answer(
        text=help_info
    )
