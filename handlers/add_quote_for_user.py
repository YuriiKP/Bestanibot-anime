import os

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

from loader import dp, bot, am, um
from texts import add_quote_text, get_keys, add_quote_info
from states import State_add_quote
from keyboards import select_type_quote
from custom_filters import IsUser, IsPidor
from custom_callbackdata import CallbackData_CheckQuote



class MyCallback(CallbackData, prefix='back'):
    step: str
    action: str


@dp.message(F.text == add_quote_text, IsPidor())
async def process_add_quote_info_pidor(message: Message, state: FSMContext):
    await message.answer(text='💤 Вам нельзя добавлять цитаты')


@dp.message(F.text == add_quote_text, IsUser())
async def process_add_quote_info(message: Message, state: FSMContext):
    await state.set_state(State_add_quote.video_file)
    
    await message.answer(
        text=add_quote_info,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⭕️ Отмена', callback_data='start')]
        ]
        )
    )

# Принимем видео
@dp.message(F.video, State_add_quote.video_file, IsUser())
async def take_video_file(message: Message, state: FSMContext):
    if int(message.video.file_size) < 5242880:
        async def peocess_msg():
            await state.update_data(file_unique_id=file_unique_id, file_id=file_id)
            await state.set_state(State_add_quote.anime_title)
            text = '<b>НАЗВАНИЕ?</b>\nСейчас отправьте название аниме\n\n<i>Также можно указать серию и таймкод аниме</i>'

            await message.answer(
                text=text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='⭕️ Отмена', callback_data='start')]
                ]
                )
            )
        

        file_unique_id = message.video.file_unique_id
        file_id = message.video.file_id
        
        if message.caption:
            qoute_data = message.caption
            qoute_data = qoute_data.split('*')
            
            if len(qoute_data) == 2:
                quote = qoute_data[0]
                anime_title = qoute_data[1]
                time_code = '-'

                await state.update_data(file_unique_id=file_unique_id, file_id=file_id, quote=quote, anime_title=anime_title, time_code=time_code)
                await state.set_state(State_add_quote.keys)

                await message.answer(
                text=get_keys,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='⭕️ Отмена', callback_data='start')]
                ]
                )
            )

            elif len(qoute_data) == 3:
                quote = qoute_data[0]
                anime_title = qoute_data[1]
                time_code = qoute_data[2]

                await state.update_data(file_unique_id=file_unique_id, file_id=file_id, quote=quote, anime_title=anime_title, time_code=time_code)
                await state.set_state(State_add_quote.keys)

                await message.answer(
                text=get_keys,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='⭕️ Отмена', callback_data='start')]
                ]
                )
            )
            
            else:
                await peocess_msg()

        else:
            await peocess_msg()

    else:
        await message.answer(
            text='Файл больше 5 МБ, отправьте заново файл меньшего размера'
        )


# Принимем название аниме
@dp.message(F.text, State_add_quote.anime_title, IsUser())
async def take_anime_title(message: Message, state: FSMContext):
    anime_title = message.text

    await state.update_data(anime_title=anime_title)
    await take_confirm_light(query=CallbackQuery(id='none', from_user=message.from_user, chat_instance='none', message=message), state=state)


# Подтверждение упрощенный вариант
@dp.callback_query(MyCallback.filter(F.action == 'confirm_quote'), IsUser())
async def take_confirm_light(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    anime_title = data['anime_title']
    file_id = data['file_id']

    text = f'<b>ПОДТВЕРДИТЕ ОТПРАВКУ ДАННЫХ НА МОДЕРАЦИЯ</b>\n\n<b>НАЗВАНИЕ АНИМЕ:</b> {anime_title}'

    await query.message.answer_video(
        video=file_id,
        caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_save_anime'),
                InlineKeyboardButton(text='⭕️ Отмена', callback_data='start')
            ],
        ]
        )
    )


# Сохраняем
@dp.callback_query(F.data == 'confirm_save_anime', IsUser())
async def storege_anime(query: CallbackQuery, state: FSMContext):    
    data = await state.get_data()

    file_unique_id = data['file_unique_id']
    file_id = data['file_id']
    anime_title = data['anime_title']
    quote = '-'
    time_code = '-'
    keys = '-'
    type = '-'

    path = os.path.join('data', 'video', f'{quote} {anime_title} {time_code}.mp4')

    await am.add_amine_qoute_moder(file_unique_id, file_id, path, quote.lower(), anime_title,
        time_code, keys, type, query.from_user.id
    )

    await query.message.answer(
        text='Благодарю, цитата ушла на модерацию.\n\n<i>По завершению проверки вы получите уведомление</i>',
    )

    await state.clear()

    # Оповещение для админов
    admins = await um.get_admins(moder=1, admin=1, main_admin=1)
    for admin in admins:
        await bot.send_message(
            chat_id=admin[0],
            text=f'<b>ПОЛЬЗОВАТЕЛЬ:</b> <a href="tg://user?id={query.from_user.id}">{query.from_user.first_name}</a>\n<b>ОТПРАВИЛ ЦИТАТУ НА МОДЕРАЦИЮ</b>', 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🔍 Проверить', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())]
            ])
        )


# Обработка отмены выбора
@dp.callback_query(MyCallback.filter(F.action == 'back'), IsUser())
async def handnding_back(query: CallbackQuery, state: FSMContext, callback_data: MyCallback):
    step = callback_data.step
    
    if step == 'process_add_quote':
        await process_add_quote(query.message, state)
    
    if step == 'take_video_file':
        await state.set_state(State_add_quote.quote)
        await query.message.answer(
            text='Отправьте заново сообщение с цитатой из видео',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='process_add_quote', action='back').pack())]
            ]
            )
        )
    
    if step == 'take_quote':
        await state.set_state(State_add_quote.anime_title)
        await query.message.answer(
            text='Отправьте заново название аниме',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_video_file', action='back').pack())]
            ]
            )
        )
    
    if step == 'take_anime_title':
        await state.set_state(State_add_quote.time_code)
        await query.message.answer(
            text='Отправьте заново <b>СЕЗОН СЕРИЮ ТАЙМКОД</b> аниме, в формате:\n1 2 5-45\nЕсли у аниме только один сезон, всё равно укажите 1',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_quote', action='back').pack())]
            ]
            )
        )
    
    if step == 'take_time_code':
        await state.set_state(State_add_quote.keys)
        await query.message.answer(
            text='Отправьте заново дополнительные ключевые слова, через запятую, чтобы другим людям было проще найти эту цитату <i>(не меньше 5)</i>\n(сама цитата и название аниме уже включенны, повторно их можно не писать)\n\nИспользуйте сайты синонимов, например: https://sinonim.org/',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_anime_title', action='back').pack())]
            ]
            )
        )

    if step == 'take_type':
        await query.message.answer(
        text='Выберите заново тип к которому цитата ближе всего\n<i>(какая тональность цитаты?)</i>',
        reply_markup=select_type_quote
    )
        





"""
#################################################################################
#################################################################################
#################################################################################
"""

class MyCallback(CallbackData, prefix='back'):
    step: str
    action: str


@dp.message(F.text == add_quote_text, IsPidor())
async def process_add_quote_info_pidor(message: Message, state: FSMContext):
    await message.answer(text='💤 Вам нельзя добавлять цитаты')


@dp.message(F.text == add_quote_text, IsUser())
async def process_add_quote_info(message: Message, state: FSMContext):
    await message.answer(
        text=add_quote_info,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ ПРОДОЛЖИТЬ', callback_data='confirm_quote_info')],
            [InlineKeyboardButton(text='⭕️ Отмена', callback_data='start')]
        ]
        )
    )


@dp.callback_query(F.data == 'confirm_quote_info', IsUser())
async def process_add_quote(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_add_quote.video_file)
    
    await query.message.answer(
        text='<b>ВИДЕО?</b>\nОтправьте видео с цитатой из аниме\n\nВ видео не должно быть ничего кроме цитаты\n\n<b>Основные характеристики видеофайла <i>(могут быть исключения)</i></b> 🎦\n📐 Разрешение видео 1920:1080, 1280:720\n🗂 Размер файла буквально пару мегабайт\n🧮 Битрейт примерно 1000 - 2500 кбит',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⭕️ Отмена', callback_data='start')]
        ]
        )
    )


# Принимем видео
@dp.message(F.video, State_add_quote.video_file, IsUser())
async def take_video_file(message: Message, state: FSMContext):
    if int(message.video.file_size) < 5242880:
        async def peocess_msg():
            await state.update_data(file_unique_id=file_unique_id, file_id=file_id)
            # await state.set_state(State_add_quote.quote)
            await state.set_state(State_add_quote.anime_title)
            # text = '<b>ЦИТАТА?</b>\nСейчас отправьте сообщение с цитатой из видео'
            text = '<b>НАЗВАНИЕ?</b>\nСейчас отправьте название аниме'

            await message.answer(
                text=text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='process_add_quote', action='back').pack())]
                ]
                )
            )
        

        file_unique_id = message.video.file_unique_id
        file_id = message.video.file_id
        
        if message.caption:
            qoute_data = message.caption
            qoute_data = qoute_data.split('*')
            
            if len(qoute_data) == 2:
                quote = qoute_data[0]
                anime_title = qoute_data[1]
                time_code = '-'

                await state.update_data(file_unique_id=file_unique_id, file_id=file_id, quote=quote, anime_title=anime_title, time_code=time_code)
                await state.set_state(State_add_quote.keys)

                await message.answer(
                text=get_keys,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_anime_title', action='back').pack())]
                ]
                )
            )

            elif len(qoute_data) == 3:
                quote = qoute_data[0]
                anime_title = qoute_data[1]
                time_code = qoute_data[2]

                await state.update_data(file_unique_id=file_unique_id, file_id=file_id, quote=quote, anime_title=anime_title, time_code=time_code)
                await state.set_state(State_add_quote.keys)

                await message.answer(
                text=get_keys,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_anime_title', action='back').pack())]
                ]
                )
            )
            
            else:
                await peocess_msg()

        else:
            await peocess_msg()

    else:
        await message.answer(
            text='Файл больше 5 МБ, отправьте заново файл меньшего размера'
        )


# Принимем цитату из видео
@dp.message(F.text, State_add_quote.quote, IsUser())
async def take_quote(message: Message, state: FSMContext):
    quote = message.text

    await state.update_data(quote=quote)
    await state.set_state(State_add_quote.anime_title)

    await message.answer(
        text='<b>НАЗВАНИЕ?</b>\nСейчас отправьте название аниме',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_video_file', action='back').pack())]
        ]
        )
    )


# Принимем название аниме
@dp.message(F.text, State_add_quote.anime_title, IsUser())
async def take_anime_title(message: Message, state: FSMContext):
    anime_title = message.text

    await state.update_data(anime_title=anime_title)
    # await state.set_state(State_add_quote.time_code)
    # text = '<b>СЕЗОН И ТАЙМКОД?</b>\nСейчас отправьте <b>СЕЗОН СЕРИЮ ТАЙМКОД</b> аниме, в формате:\n1 2 5-45\nЕсли у аниме только один сезон, всё равно укажите 1\n\n<i>Можно пропустить, отправьте прочерк -</i>'

    # await message.answer(
    #     text=text,
    #     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    #         [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_quote', action='back').pack())]
    #     ]
    #     )
    # )

    await take_confirm_light(query=CallbackQuery(id='none', from_user=message.from_user, chat_instance='none', message=message), state=state)



# Принимем таймкод
@dp.message(F.text, State_add_quote.time_code, IsUser())
async def take_time_code(message: Message, state: FSMContext):
    time_code = message.text

    await state.update_data(time_code=time_code)
    await state.set_state(State_add_quote.keys)

    await message.answer(
        text=get_keys,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_anime_title', action='back').pack())]
        ]
        )
    )


# Выбор тональности
@dp.message(F.text, State_add_quote.keys, IsUser())
async def take_type(message: Message, state: FSMContext):
    keys = message.text

    await state.update_data(keys=keys)

    await message.answer(
        text='<b>ТИП?</b>\nИ последнее, выберите тип к которому цитата ближе всего\n<i>(какая тональность цитаты?)</i>',
        reply_markup=select_type_quote
    )


# Подтверждение
@dp.callback_query(MyCallback.filter(F.action == 'type'), IsUser())
async def take_confirm(query: CallbackQuery, state: FSMContext, callback_data: MyCallback):
    data = await state.get_data()

    quote = data['quote']
    anime_title = data['anime_title']
    time_code = data['time_code']
    keys = data['keys']
    
    type = callback_data.step
    await state.update_data(type=type)

    text = f'<b>ПОДТВЕРДИТЕ ОТПРАВКУ ДАННЫХ НА МОДЕРАЦИЯ</b>\n\n<b>ЦИТАТА:</b> {quote}\n<b>НАЗВАНИЕ АНИМЕ:</b> {anime_title}\n<b>ТАЙКОД:</b> {time_code}\n<b>КЛЮЧИ:</b> {keys}\n<b>ТИП:</b> {type}'

    await query.message.answer(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_save_anime'),
                InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_type', action='back').pack()),
            ],
        ]
        )
    )


# Подтверждение упрощенный вариант
@dp.callback_query(MyCallback.filter(F.action == 'confirm_quote'), IsUser())
async def take_confirm_light(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    anime_title = data['anime_title']
    file_id = data['file_id']

    text = f'<b>ПОДТВЕРДИТЕ ОТПРАВКУ ДАННЫХ НА МОДЕРАЦИЯ</b>\n\n<b>НАЗВАНИЕ АНИМЕ:</b> {anime_title}'

    await query.message.answer_video(
        video=file_id,
        caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_save_anime'),
                InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_type', action='back').pack()),
            ],
        ]
        )
    )


# Сохраняем
@dp.callback_query(F.data == 'confirm_save_anime', IsUser())
async def storege_anime(query: CallbackQuery, state: FSMContext):    
    data = await state.get_data()

    file_unique_id = data['file_unique_id']
    file_id = data['file_id']
    quote = data['quote']
    anime_title = data['anime_title']
    time_code = data['time_code']
    keys = data['keys']
    type = data['type']

    path = os.path.join('data', 'video', f'{quote} {anime_title} {time_code}.mp4')

    await am.add_amine_qoute_moder(file_unique_id, file_id, path, quote.lower(), anime_title,
        time_code, keys, type, query.from_user.id
    )

    await query.message.answer(
        text='Благодарю, цитата ушла на модерацию.\n\n<i>По завершению проверки вы получите уведомление</i>',
    )

    await state.clear()

    # Оповещение для админов
    admins = await um.get_admins(moder=1, admin=1, main_admin=1)
    for admin in admins:
        await bot.send_message(
            chat_id=admin[0],
            text=f'<b>ПОЛЬЗОВАТЕЛЬ:</b> <a href="tg://user?id={query.from_user.id}">{query.from_user.first_name}</a>\n<b>ОТПРАВИЛ ЦИТАТУ НА МОДЕРАЦИЮ</b>', 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🔍 Проверить', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())]
            ])
        )


# Обработка отмены выбора
@dp.callback_query(MyCallback.filter(F.action == 'back'), IsUser())
async def handnding_back(query: CallbackQuery, state: FSMContext, callback_data: MyCallback):
    step = callback_data.step
    
    if step == 'process_add_quote':
        await process_add_quote(query.message, state)
    
    if step == 'take_video_file':
        await state.set_state(State_add_quote.quote)
        await query.message.answer(
            text='Отправьте заново сообщение с цитатой из видео',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='process_add_quote', action='back').pack())]
            ]
            )
        )
    
    if step == 'take_quote':
        await state.set_state(State_add_quote.anime_title)
        await query.message.answer(
            text='Отправьте заново название аниме',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_video_file', action='back').pack())]
            ]
            )
        )
    
    if step == 'take_anime_title':
        await state.set_state(State_add_quote.time_code)
        await query.message.answer(
            text='Отправьте заново <b>СЕЗОН СЕРИЮ ТАЙМКОД</b> аниме, в формате:\n1 2 5-45\nЕсли у аниме только один сезон, всё равно укажите 1',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_quote', action='back').pack())]
            ]
            )
        )
    
    if step == 'take_time_code':
        await state.set_state(State_add_quote.keys)
        await query.message.answer(
            text='Отправьте заново дополнительные ключевые слова, через запятую, чтобы другим людям было проще найти эту цитату <i>(не меньше 5)</i>\n(сама цитата и название аниме уже включенны, повторно их можно не писать)\n\nИспользуйте сайты синонимов, например: https://sinonim.org/',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='👈 Назад', callback_data=MyCallback(step='take_anime_title', action='back').pack())]
            ]
            )
        )

    if step == 'take_type':
        await query.message.answer(
        text='Выберите заново тип к которому цитата ближе всего\n<i>(какая тональность цитаты?)</i>',
        reply_markup=select_type_quote
    )