from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from loader import dp, bot, am, um
from texts import qoutes_moder, get_keys
from states import State_check_true_msg, State_check_false_msg, State_edit_quote_moder
from custom_callbackdata import CallbackData_CheckQuote
from custom_filters import IsModer
from keyboards import MyCallback



# Все цитаты на проверке
@dp.message(F.text == qoutes_moder, IsModer())
async def show_all_quotes_moder(message: Message, state: FSMContext):
    quotes = await am.get_anime_quotes_moder()

    if quotes:
        await message.answer(
            text=f'<b>ВСЕГО ЦИТАТ:</b> {len(quotes)}',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🔍 Проверить', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=quotes[0][0]).pack())]
            ])
        )
    else:
        await message.answer(
            text='Пусто'
        )


# Посмотреть цитату
@dp.callback_query(CallbackData_CheckQuote.filter(F.action == 'check_quote'), IsModer())
async def process_check_quote(query: CallbackQuery, state: FSMContext, callback_data: CallbackData_CheckQuote):
    await state.clear()

    await query.message.delete()

    file_unique_id = callback_data.file_unique_id
    anime_quote = await am.get_anime_quote_moder_by_id(file_unique_id)
    await state.update_data(user_id=anime_quote[8], file_unique_id=file_unique_id)

    quote = anime_quote[3]
    anime_title = anime_quote[4]
    time_code = anime_quote[5]
    keys = anime_quote[6]
    type = anime_quote[7]
    user_id_creator = anime_quote[8]

    text = f'<a href="tg://user?id={user_id_creator}">Пользователь</a>\n\n<b>ЦИТАТА:</b> {quote}\n<b>НАЗВАНИЕ АНИМЕ:</b> {anime_title}\n<b>ТАЙКОД:</b> {time_code}\n<b>КЛЮЧИ:</b> {keys}\n<b>ТИП:</b> {type}'

    await query.message.answer_video(
        video=anime_quote[1],
        caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Одобрить', callback_data=CallbackData_CheckQuote(action='true', file_unique_id=file_unique_id).pack())],
            [InlineKeyboardButton(text='❌ Отклонить', callback_data=CallbackData_CheckQuote(action='false', file_unique_id=file_unique_id).pack())],
            [InlineKeyboardButton(text='📝 Редактировать', callback_data=CallbackData_CheckQuote(action='edit', file_unique_id=file_unique_id).pack())],
            [InlineKeyboardButton(text='🍌 ПОШЕЛ НАХ*Й', callback_data=CallbackData_CheckQuote(action='ban', file_unique_id=file_unique_id).pack())],
        ])
    )


##################################
#######--ОДОБРЕНИЕ ЦИТАТЫ--#######
##################################

# Сопроводительное сообщение
@dp.callback_query(CallbackData_CheckQuote.filter(F.action == 'true'), IsModer())
async def check_quote_true_msg(query: CallbackQuery, state: FSMContext, callback_data: CallbackData_CheckQuote):
    await state.set_state(State_check_true_msg.msg)
    
    data = await state.get_data()

    await query.message.answer(
        text='Напишите сопроводительное сообщение для автора цитаты:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='➡️ Пропустить', callback_data='skip_true_msg')],
            [InlineKeyboardButton(text='👈 Назад', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=data['file_unique_id']).pack())],
        ])
    )


# Пропустить сопроводительное сообщение
@dp.callback_query(F.data == 'skip_true_msg', IsModer())
async def skip_true_msg(query: CallbackQuery, state: FSMContext):
    text = '<b>🫡 Ваша цитата прошла модерацию и добавленна в бота, спасибо</b>'
    await state.update_data(msg=text)

    await query.message.answer(
        text=f'<b>СООБЩЕНИЕ ДЛЯ ПОЛЬЗОВАТЕЛЯ:</b>\n{text}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⬆️ Отправить', callback_data='send_true_msg')],
            [InlineKeyboardButton(text='👈 Назад', callback_data=CallbackData_CheckQuote(action='true', file_unique_id='0').pack())],
        ])
    )


# Принимаем сопроводительное сообщение
@dp.message(State_check_true_msg.msg, IsModer())
async def msg_true(message: Message, state: FSMContext):
    msg =  f'<b>🫡 Ваша цитата прошла модерацию и добавленна в бота, спасибо</b>\n\n{message.text}'
    
    await state.update_data(msg=msg)

    await message.answer(
        text=msg,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⬆️ Отправить', callback_data='send_true_msg')],
            [InlineKeyboardButton(text='👈 Назад', callback_data=CallbackData_CheckQuote(action='true', file_unique_id='0').pack())],
        ])
    )


# Отправляем оповещение пользователю и добавляем цитату в бота
@dp.callback_query(F.data == 'send_true_msg', IsModer())
async def send_true_msg(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    
    msg = data['msg']
    user_id = data['user_id']
    file_unique_id = data['file_unique_id']

    # Переносим цитату
    anime_quote = await am.get_anime_quote_moder_by_id(file_unique_id)
    await am.del_anime_quote_moder_by_id(file_unique_id)
    await am.add_amine_qoute(
        file_unique_id=anime_quote[0], 
        file_id=anime_quote[1], 
        file_path=anime_quote[2],
        quote=anime_quote[3],
        anime_title=anime_quote[4],
        time_code=anime_quote[5],
        keys=anime_quote[6],
        type=anime_quote[7],
        user_id=anime_quote[8]
    )
    # Обновляем инфу и качаем файл
    await bot.download(file=anime_quote[1], destination=anime_quote[2])
    await um.update_user(anime_quote[8], count_anime=1)

    await query.message.delete()
    await query.answer(
        text='Сообщение отправленно'
    )

    await bot.send_message(
        chat_id=user_id,
        text=msg
    )


###################################
#######--ОТКЛОНЕНИЕ ЦИТАТЫ--#######
###################################

@dp.callback_query(CallbackData_CheckQuote.filter(F.action == 'false'), IsModer())
async def check_quote_false_msg(query: CallbackQuery, state: FSMContext, callback_data: CallbackData_CheckQuote):
    await state.set_state(State_check_false_msg.msg)
    
    data = await state.get_data()

    await query.message.answer(
        text='Напишите сопроводительное сообщение для автора цитаты:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='👈 Назад', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=data['file_unique_id']).pack())],
        ])
    )


# Принимаем сопроводительное сообщение
@dp.message(State_check_false_msg.msg, IsModer())
async def msg_true(message: Message, state: FSMContext):
    await state.update_data(msg=f'<b>😔 Ваша цитата не прошла модерацию</b>\n\n{message.text}')

    await message.answer(
        text=f'<b>СООБЩЕНИЕ ДЛЯ ПОЛЬЗОВАТЕЛЯ:</b>\n{message.text}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⬆️ Отправить', callback_data='send_false_msg')],
            [InlineKeyboardButton(text='👈 Назад', callback_data=CallbackData_CheckQuote(action='false', file_unique_id='0').pack())],
        ])
    )


# Отправляем оповещение пользователю и добавляем цитату в бота
@dp.callback_query(F.data == 'send_false_msg', IsModer())
async def send_false_msg(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    msg = data['msg']
    user_id = data['user_id']
    file_unique_id = data['file_unique_id']

    await am.del_anime_quote_moder_by_id(file_unique_id)

    await query.message.delete()
    await query.answer(
        text='Сообщение отправленно'
    )

    await bot.send_message(
        chat_id=user_id,
        text=msg
    )


################################
#######--РЕДАКТИРОВАНИЕ--#######
################################

# Отправить цитату
async def send_msg_quote(user_id, file_unique_id):
    # Формируем сообщение с цитатой
    anime_quote = await am.get_anime_quote_moder_by_id(file_unique_id)
    
    quote = anime_quote[3]
    anime_title = anime_quote[4]
    time_code = anime_quote[5]
    keys = anime_quote[6]
    type = anime_quote[7]
    user_id_creator = anime_quote[8]

    text = f'<a href="tg://user?id={user_id_creator}">Пользователь</a>\n\n<b>ЦИТАТА:</b> {quote}\n<b>НАЗВАНИЕ АНИМЕ:</b> {anime_title}\n<b>ТАЙКОД:</b> {time_code}\n<b>КЛЮЧИ:</b> {keys}\n<b>ТИП:</b> {type}'

    # Отправляем в чат
    await bot.send_video(
        chat_id=user_id,
        video=anime_quote[1],
        caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Заменить видео', callback_data='video_file')],
            [InlineKeyboardButton(text='Изменить цитату', callback_data='quote')],
            [InlineKeyboardButton(text='Изменить название аниме', callback_data='anime_title')],
            [InlineKeyboardButton(text='Изменить таймкод', callback_data='time_code')],
            [InlineKeyboardButton(text='Изменить ключи', callback_data='keys')],
            [InlineKeyboardButton(text='Изменить тип', callback_data='type')],
            [InlineKeyboardButton(text='👈 Назад', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())],
        ]))


# Редактируем клавиатуру
@dp.callback_query(CallbackData_CheckQuote.filter(F.action == 'edit'), IsModer())
async def check_quote_edit(query: CallbackQuery, state: FSMContext, callback_data: CallbackData_CheckQuote):    
    file_unique_id = callback_data.file_unique_id
    await state.clear()
    await state.update_data(file_unique_id=file_unique_id)
    
    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Заменить видео', callback_data='video_file')],
        [InlineKeyboardButton(text='Изменить цитату', callback_data='quote')],
        [InlineKeyboardButton(text='Изменить название аниме', callback_data='anime_title')],
        [InlineKeyboardButton(text='Изменить таймкод', callback_data='time_code')],
        [InlineKeyboardButton(text='Изменить ключи', callback_data='keys')],
        [InlineKeyboardButton(text='Изменить тип', callback_data='type')],
        [InlineKeyboardButton(text='👈 Назад', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())],
    ]))



################################################################################
# Замена видео
@dp.callback_query(F.data == 'video_file', IsModer())
async def process_change_video(query: CallbackQuery, state: FSMContext):
    await query.message.delete()

    await state.set_state(State_edit_quote_moder.video_file)
    data = await state.get_data()
    file_unique_id = data['file_unique_id']

    await query.message.answer(
        text='Отправьте новый видеофайл:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❌ Отмена', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())]
        ])
    )

# Принимаем видео
@dp.message(F.video, State_edit_quote_moder.video_file, IsModer())
async def take_video_file(message: Message, state: FSMContext):
    if int(message.video.file_size) < 5242880:
        await message.delete()
        data = await state.get_data()
        file_unique_id = data['file_unique_id']
        
        await state.clear()
        
        file_unique_id_2 = message.video.file_unique_id
        file_id = message.video.file_id

        await state.update_data(file_unique_id=file_unique_id_2)

        await am.update_amine_qoute_moder(
            file_unique_id=file_unique_id,
            file_unique_id_2=file_unique_id_2,
            file_id=file_id
        )

        # Отправляем измененную цитату
        await send_msg_quote(message.from_user.id, file_unique_id_2)

    else:
        await message.answer(
            text='Файл больше 5 МБ, отправьте заново файл меньшего размера'
        )



################################################################################
# Замена цитаты
@dp.callback_query(F.data == 'quote', IsModer())
async def process_change_quote(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_edit_quote_moder.quote)
    data = await state.get_data()
    file_unique_id = data['file_unique_id']

    await query.message.answer(
        text='Отправьте новый текст цитаты:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❌ Отмена', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())]
        ])
    )


# Принимаем новый текст цитаты
@dp.message(State_edit_quote_moder.quote, IsModer())
async def take_new_qoute(message: Message, state: FSMContext):
    data = await state.get_data()
    file_unique_id = data['file_unique_id']
    await state.clear()

    await am.update_amine_qoute_moder(
        file_unique_id=file_unique_id,
        quote=message.text
    )

    # Отправляем цитату
    await state.update_data(file_unique_id=file_unique_id)
    await send_msg_quote(message.from_user.id, file_unique_id)



################################################################################
# Замена названия аниме
@dp.callback_query(F.data == 'anime_title', IsModer())
async def process_change_anime_title(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_edit_quote_moder.anime_title)
    data = await state.get_data()
    file_unique_id = data['file_unique_id']

    await query.message.answer(
        text='Отправьте новое название аниме:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❌ Отмена', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())]
        ])
    )


# Принимаем новое название аниме
@dp.message(State_edit_quote_moder.anime_title, IsModer())
async def take_new_anime_title(message: Message, state: FSMContext):
    data = await state.get_data()
    file_unique_id = data['file_unique_id']
    await state.clear()

    await am.update_amine_qoute_moder(
        file_unique_id=file_unique_id,
        anime_title=message.text
    )

    # Отправляем цитату
    await state.update_data(file_unique_id=file_unique_id)
    await send_msg_quote(message.from_user.id, file_unique_id)



################################################################################
# Замена таймкода
@dp.callback_query(F.data == 'time_code', IsModer())
async def process_change_time_code(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_edit_quote_moder.time_code)
    data = await state.get_data()
    file_unique_id = data['file_unique_id']

    await query.message.answer(
        text='Отправьте сезон, серию и таймкод аниме, в формате:\n1 2 5-45:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❌ Отмена', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())]
        ])
    )


# Принимаем новый таймкод
@dp.message(State_edit_quote_moder.time_code, IsModer())
async def take_new_time_code(message: Message, state: FSMContext):
    data = await state.get_data()
    file_unique_id = data['file_unique_id']
    await state.clear()

    await am.update_amine_qoute_moder(
        file_unique_id=file_unique_id,
        time_code=message.text
    )

    # Отправляем цитату
    await state.update_data(file_unique_id=file_unique_id)
    await send_msg_quote(message.from_user.id, file_unique_id)



################################################################################
# Замена ключей
@dp.callback_query(F.data == 'keys', IsModer())
async def process_change_keys(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_edit_quote_moder.keys)
    data = await state.get_data()
    file_unique_id = data['file_unique_id']

    await query.message.answer(
        text=get_keys,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❌ Отмена', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())]
        ])
    )


# Принимаем новые ключи
@dp.message(State_edit_quote_moder.keys, IsModer())
async def take_new_keys(message: Message, state: FSMContext):
    data = await state.get_data()
    file_unique_id = data['file_unique_id']
    await state.clear()

    await am.update_amine_qoute_moder(
        file_unique_id=file_unique_id,
        keys=message.text
    )

    # Отправляем цитату
    await state.update_data(file_unique_id=file_unique_id)
    await send_msg_quote(message.from_user.id, file_unique_id)




################################################################################
# Замена типа цитаты
@dp.callback_query(F.data == 'type', IsModer())
async def process_change_type(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_edit_quote_moder.keys)
    data = await state.get_data()
    file_unique_id = data['file_unique_id']

    select_type_quote_moder = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='😄 Радость', callback_data=MyCallback(step='радость', action='type_moder').pack()), InlineKeyboardButton(text='😘 Хвалить', callback_data=MyCallback(step='хвалить', action='type_moder').pack()),],
            [InlineKeyboardButton(text='😔 Грусть', callback_data=MyCallback(step='грусть', action='type_moder').pack()), InlineKeyboardButton(text='🤯 Ругать', callback_data=MyCallback(step='ругать', action='type_moder').pack()),],
            [InlineKeyboardButton(text='😍 Любовь', callback_data=MyCallback(step='любовь', action='type_moder').pack()), InlineKeyboardButton(text='😡 Злость', callback_data=MyCallback(step='злость', action='type_moder').pack()),],
            [InlineKeyboardButton(text='🥺 Прощание', callback_data=MyCallback(step='прощание', action='type_moder').pack()), InlineKeyboardButton(text=' 😉 Согласие', callback_data=MyCallback(step='согласие', action='type_moder').pack()),],
            [InlineKeyboardButton(text='🤗 Приветствие', callback_data=MyCallback(step='приветствие', action='type_moder').pack()), InlineKeyboardButton(text='🫣 Отрицание', callback_data=MyCallback(step='отрицание', action='type_moder').pack()),],
            [InlineKeyboardButton(text='❌ Отмена', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())]
        ]   
    )

    await query.message.answer(
        text='Выберите тип к которому цитата ближе всего\n<i>(какая тональность цитаты?)</i>',
        reply_markup=select_type_quote_moder,
    )


# Обновляем тим цитаты
@dp.callback_query(MyCallback.filter(F.action == 'type_moder'), IsModer())
async def take_new_type(query: CallbackQuery, state: FSMContext, callback_data: MyCallback):
    type = callback_data.step
    
    data = await state.get_data()
    file_unique_id = data['file_unique_id']
    await state.clear()

    await am.update_amine_qoute_moder(
        file_unique_id=file_unique_id,
        type=type
    )

    # Отправляем цитату
    await state.update_data(file_unique_id=file_unique_id)
    await send_msg_quote(query.from_user.id, file_unique_id)



#####################
#######--БАН--#######
#####################

# Бан пользователя
@dp.callback_query(CallbackData_CheckQuote.filter(F.action == 'ban'), IsModer())
async def check_quote_ban(query: CallbackQuery, state: FSMContext, callback_data: CallbackData_CheckQuote):    
    data = await state.get_data()
    file_unique_id = data['file_unique_id']

    await query.message.answer(
        text='Забанить пользователя ',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🍌 Бан', callback_data='ban_user')],
            [InlineKeyboardButton(text='❌ Отмена', callback_data=CallbackData_CheckQuote(action='check_quote', file_unique_id=file_unique_id).pack())],
        ])
    )


# Подтверждение бана
@dp.callback_query(F.data == 'ban_user', IsModer())
async def check_quote_ban_confirm(query: CallbackQuery, state: FSMContext):    
    data = await state.get_data()
    file_unique_id = data['file_unique_id']

    quote_data = await am.get_anime_quote_moder_by_id(file_unique_id)
    user_id = quote_data[8]

    await um.update_user(
        id=user_id,
        status_user='pidor'
    )

    await am.del_all_anime_quote_moder(user_id)

    await query.message.answer(
        text=f'<a href="tg://user?id={user_id}">Пользователь</a> забанен',
    )