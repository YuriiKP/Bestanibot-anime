from random import randint

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from loader import bot, dp, am


# Случайная цитата, в лс или в чате
@dp.message(Command('rand'))
async def random_quote(message: Message, state: FSMContext):
    quote = await am.random_anime_quote()

    await message.answer_video(
        video=quote[1]
    )


# Ответ на сообщение в чате цитатой
@dp.message(Command('quote'), F.reply_to_message)
async def reply_message_group(message: Message, state: FSMContext):
    if message.reply_to_message.text:
        raw_msg_text = message.reply_to_message.text.lower()
        
        translation = raw_msg_text.maketrans(
            {
                ord(','): '', ord('.'): '', ord(')'): '', ord('('): '', ord(':'): '',
            })
        msg_text = raw_msg_text.translate(translation)
        
        list_msg_text = msg_text.split(' ')
        
        # Проверка длины текста для поиска цитаты
        if len(list_msg_text) > 2:
            msg_text = ' '.join((list_msg_text[0], list_msg_text[1]))

        # Находим цитату, если нет то берем рандомную
        quotes = await am.get_anime_quotes(msg_text, 1)
        if quotes:
            quote = quotes[randint(0, len(quotes)-1)]    
        else:
            quote = await am.random_anime_quote()
    else:
        quote = await am.random_anime_quote()
    
    await bot.send_video(
        chat_id=message.chat.id,
        video=quote[1],
        reply_to_message_id=message.reply_to_message.message_id
    )