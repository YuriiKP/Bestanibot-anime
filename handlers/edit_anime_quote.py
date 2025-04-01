import os

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import dp, bot, am
from texts import edit_qoute_button
from states import State_Edit_Amine_Quotes
from custom_filters import IsAdmin

# Главною мнею редактирования
@dp.message(F.text == edit_qoute_button, IsAdmin())
async def edit_quote_menu(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(offset=0) # Смещение по цитатм во время редактирования

    count_quotes = await am.count_anime_quote()

    await message.answer(
        text=f'Всего цитат: {count_quotes}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Редактировать все цитаты', callback_data='edit_all_quotes')]
        ])
    )


##############
# Редактирование всех цитат по порядку (список редактируемых цитат будет храниться в памяти)
@dp.callback_query(F.data == 'edit_all_quotes', IsAdmin())
async def edit_all_quotes(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_Edit_Amine_Quotes.settings_quote)

    offset = (await state.get_data())['offset']
    all_anime_quotes = await am.all_anime_quotes()

    builder = InlineKeyboardBuilder()
    if offset == len(all_anime_quotes)-1:
        builder.button(text='Заменить видео', callback_data='edit_video_quote')
        builder.button(text='Поменять инфо', callback_data='edit_info_quote')
        builder.button(text='Назад', callback_data='back_video_quote')
        builder.button(text='Перейти к', callback_data='select_video_quote')
    elif offset == 0:
        builder.button(text='Заменить видео', callback_data='edit_video_quote')
        builder.button(text='Поменять инфо', callback_data='edit_info_quote')
        builder.button(text='Дальше', callback_data='skip_video_quote')
        builder.button(text='Перейти к', callback_data='select_video_quote')
    else:
        builder.button(text='Заменить видео', callback_data='edit_video_quote')
        builder.button(text='Поменять инфо', callback_data='edit_info_quote')
        builder.button(text='Дальше', callback_data='skip_video_quote')
        builder.button(text='Назад', callback_data='back_video_quote')
        builder.button(text='Перейти к', callback_data='select_video_quote')
 
    builder.adjust(1)
        
    anime_quote = all_anime_quotes[offset]
    await state.update_data(file_unique_id=anime_quote[0])

    file_id = anime_quote[1]
    quote = anime_quote[3]
    anime_title = anime_quote[4]
    time_code = anime_quote[5]
    keys = anime_quote[6]
    type = anime_quote[7]
    author = anime_quote[8]

    text = f'№ {offset+1} из {len(all_anime_quotes)}\n\n<b>ЦИТАТА:</b> {quote}\n\n<b>АНИМЕ:</b> {anime_title}\n\n<b>ТАЙМКОД:</b> {time_code}\n\n<b>КЛЮЧИ:</b> {keys}\n\n<b>ТИП:</b> {type}\n\n<b><a href="tg://user?id={author}">АВТОР</a></b>'
    if len(text) > 1000:
        correction = len(text) - 1000
        text = f'№ {offset+1} из {len(all_anime_quotes)}\n\n<b>ЦИТАТА:</b> {quote}\n\n<b>АНИМЕ:</b> {anime_title}\n\n<b>ТАЙМКОД:</b> {time_code}\n\n<b>КЛЮЧИ:</b> {keys[:-correction]}\n\n<b>ТИП:</b> {type}\n\n<b><a href="tg://user?id={author}">АВТОР</a></b>'

    await query.message.answer_video(
        video=file_id,
        caption=text,
        reply_markup=builder.as_markup(),
    )

##############
# Замена видео
@dp.callback_query(F.data == 'edit_video_quote', IsAdmin())
async def edit_video_quote(query: CallbackQuery, state: FSMContext):
    await query.message.answer(text='Отправьте видео с цитатой')
    await state.set_state(State_Edit_Amine_Quotes.video)

# Принимаем новое видео 
@dp.message(F.video, State_Edit_Amine_Quotes.video, IsAdmin())
async def take_video_quote(message: Message, state: FSMContext):
    data = await state.get_data()
    offset = data['offset']
    file_unique_id = data['file_unique_id']

    await message.delete()
    
    await am.update_amine_qoute(
        file_unique_id=file_unique_id,
        file_unique_id_2=message.video.file_unique_id,
        file_id=message.video.file_id
    )

    # Качаем видео на диск
    anime_quote = await am.get_anime_quote_by_id(message.video.file_unique_id)
    await bot.download(
        file=message.video,
        destination=anime_quote[2]
    )

    await edit_all_quotes(query=CallbackQuery(id='none', from_user=message.from_user, chat_instance='none', message=message), state=state)


###################
# Замена информации
@dp.callback_query(F.data == 'edit_info_quote', IsAdmin())
async def edit_info_quote(query: CallbackQuery, state: FSMContext):
    await query.message.answer(text='Отправьте информацию о цитате в формате: \n<b>ЦИТАТА*НАЗВАНИЕ АНИМЕ*ТАЙМКОД*КЛЮЧИ*ТИП</b>\n\n<i>Типы цитат:\nрадость\nгрусть\nлюбовь\nпрощание\nприветствие\nхвалить\nругать\nзлость\nсогласие\nотрицание</i>')
    await state.set_state(State_Edit_Amine_Quotes.quote_info)

# Принимаем инфо 
@dp.message(F.text, State_Edit_Amine_Quotes.quote_info, IsAdmin())
async def take_info_quote(message: Message, state: FSMContext):
    quote_types = ['радость', 'грусть', 'любовь', 'прощание', 'приветствие', 'хвалить', 'ругать', 'злость', 'согласие', 'отрицание']
    
    data = await state.get_data()
    offset = data['offset']
    file_unique_id = data['file_unique_id']
    
    raw_text = message.text.split('*')

    if len(raw_text) != 5:
        await message.answer(text='Ошибка, попробуйте ещё раз')
    
    elif raw_text[4].strip() not in quote_types:
        await message.answer(text='Ошибка, указан несуществующий тип цитаты')
    
    else:
        quote = raw_text[0].strip()
        anime_title = raw_text[1].strip()
        time_code = raw_text[2].strip()
        keys = raw_text[3].strip()
        type = raw_text[4].strip()
        
        # Переименовываем видео с цитатой на диске
        old_anime_quote = await am.get_anime_quote_by_id(file_unique_id)
        quote = quote[0].upper() + quote[1:]
        new_path = os.path.join('data', 'video', f'{quote} {anime_title} {time_code}.mp4')
        os.rename(old_anime_quote[2], new_path)
        
        await am.update_amine_qoute(
            file_unique_id=file_unique_id,
            file_path=new_path,
            quote=quote,
            anime_title=anime_title,
            time_code=time_code,
            keys=keys,
            type=type
        )

        await edit_all_quotes(query=CallbackQuery(id='none', from_user=message.from_user, chat_instance='none', message=message), state=state)


##################
# Следующая цитата
@dp.callback_query(F.data == 'skip_video_quote', IsAdmin())
async def skip_video_quote(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    offset = data['offset']
    offset += 1
    await state.update_data(offset=offset)

    await edit_all_quotes(query, state)


##################
# Предыдущая цитата
@dp.callback_query(F.data == 'back_video_quote', IsAdmin())
async def back_video_quote(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    offset = data['offset']
    offset -= 1
    await state.update_data(offset=offset)

    await edit_all_quotes(query, state)


##################
# Выбираем цитату
@dp.callback_query(F.data == 'select_video_quote', IsAdmin())
async def select_video_quote(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_Edit_Amine_Quotes.select_quote)
    await query.message.answer(
        text='Отправьте номер цитаты к которой перейти:'
    )

# Принимаем номер цитаты 
@dp.message(F.text, State_Edit_Amine_Quotes.select_quote, IsAdmin())
async def take_select_quote(message: Message, state: FSMContext):
    await message.delete()
    try:
        index = int(message.text)-1

        if index < 0:
            await message.answer(text='Введите корректное число')

        all_anime_quotes = await am.all_anime_quotes()
        if index > len(all_anime_quotes)-1:
            await message.answer(text='Введите корректное число')
        else:
            await state.update_data(offset=index)
            await edit_all_quotes(query=CallbackQuery(id='none', from_user=message.from_user, chat_instance='none', message=message), state=state)
    
    except ValueError:
        await message.answer(text='Введите корректное число')