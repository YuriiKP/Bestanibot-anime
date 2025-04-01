import asyncio
import logging

from aiogram import filters, F
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, BotCommandScopeDefault, BotCommandScopeAllGroupChats
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, SwitchInlineQueryChosenChat, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter
from aiogram.filters import CommandObject, JOIN_TRANSITION
from aiogram.exceptions import TelegramForbiddenError

from loader import dp, bot, db, um, gm, ADMIN_ID, CHANEL_USERNAME, deep_links_admin_manage
from texts import about_bot, chat_info
from handlers import dp
from keyboards import main_admin_menu, admin_menu, moder_menu, user_menu, pidor_menu
from custom_filters import IsMainAdmin
from commands import user_commands, chat_commands



# Старт с диплинком
@dp.message(filters.CommandStart(deep_link=True))
async def process_start_bot_deep_link(message: Message, state: FSMContext, command: CommandObject):    
    args = command.args
    
    if args in deep_links_admin_manage:
        status_user = deep_links_admin_manage[args]
        del deep_links_admin_manage[args]

        await um.update_user(
            id=message.from_user.id,
            status_user=status_user
        )

        await message.answer(
            text=f'Поздравляю! Теперь ты {status_user}'
        )

        await func_process_start_bot(message, message.from_user.id, message.from_user.first_name)
    
    else:
        await func_process_start_bot(message, message.from_user.id, message.from_user.first_name)


# Стартуем
@dp.message(filters.CommandStart())
async def process_start_bot(message: Message, state: FSMContext):
    # Сохраняем пользователя в базе
    # await um.add_new_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    await state.clear()
    await func_process_start_bot(message, message.from_user.id, message.from_user.first_name)


# Для перехода из инлайн кнопки
@dp.callback_query(F.data == 'start')
async def inline_process_start_bot(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.clear()
    await func_process_start_bot(query.message, query.from_user.id, query.from_user.first_name)


async def func_process_start_bot(query_msg: Message, user_id, first_name):
    user_info = await um.get_user(user_id)
    # Проверка подписки
    user_chat_info = await bot.get_chat_member(
        chat_id=CHANEL_USERNAME, 
        user_id=int(user_id),
    )
    
    if user_chat_info.status == 'left' or user_chat_info.status == 'kicked':
        await bot.send_message(
            chat_id=user_id,
            text='✅ Подпишись на канал https://t.me/KYuCode, чтобы продолжить пользоваться ботом',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='🔎 Проверить подписку', callback_data='start')]
                ]
            )
        )
    
    else:
        await bot.set_my_commands(
        commands=user_commands,
        scope=BotCommandScopeDefault()
        )

        await bot.set_my_commands(
        commands=chat_commands,
        scope=BotCommandScopeAllGroupChats()
        )

        if user_info[6] == 'main_admin':
            markup = main_admin_menu
        if user_info[6] == 'admin': 
            markup = admin_menu
        if user_info[6] == 'moder': 
            markup = moder_menu
        if user_info[6] == 'user': 
            markup = user_menu
        if user_info[6] == 'pidor': 
            markup = pidor_menu
        
        await query_msg.answer(
            text=f'Привет, {first_name}!',
            reply_markup=markup
        )

        # Клавиатура для быстрого старта
        inline_markup = InlineKeyboardMarkup(
            inline_keyboard= [
                [InlineKeyboardButton(text='🤖 Отправить боту', switch_inline_query_current_chat='')],
                [InlineKeyboardButton(text='💬 Отправить в чат', switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                    allow_channel_chats=True, 
                    allow_group_chats=True, 
                    allow_user_chats=True
                    ))],
                [InlineKeyboardButton(text='📌 Добавить бота в группу', url='https://t.me/bestanibot?startgroup')],
            ]
        )

        # await query_msg.answer(
        #     text=about_bot,
        #     reply_markup=inline_markup
        # )
        
        await query_msg.answer_video(
            video='BAACAgIAAxkBAAIUE2ZCBlN58yW4Umj88PC03NbpTF0JAAJ0TQAC_gMRStssLC_-p5TjNQQ',
            caption=about_bot,
            reply_markup=inline_markup
        )
        

# Добавление бота в чат
####################################################
@dp.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def add_bot_chat(event: ChatMemberUpdated):
    await bot.set_my_commands(
        commands=chat_commands,
        scope=BotCommandScopeAllGroupChats()
        )
     
    try:
        await event.answer(text=chat_info)
        chat_member_count = await bot.get_chat_member_count(event.chat.id)
        await gm.add_group(event.chat.id, event.chat.title, event.chat.username, event.chat.bio, chat_member_count)

        # Оповещение 
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f'<b>БОТА ДОБАВИЛИ В ЧАТ</b>:\nЮзернейм: {event.chat.username}\nНазвание: {event.chat.title}\nОписание: {event.chat.bio}\nКол-во пользователей: {chat_member_count}'
        )
    except TelegramForbiddenError:
        pass



####ДЛЯ ОПРЕДЕЛЕНИЯ ID МЕДИАФАЙЛА НА СЕРВЕРЕ ТГ####
####################################################
@dp.message(filters.Command('det'), IsMainAdmin())
async def process_start_bot(message: Message, state: FSMContext):     
    if message.photo:
        print(message.photo[-1].file_id)
        await message.answer(
            text=f'file_id = {message.photo[-1].file_id}\n\n'
            )
    
    if message.video:
        if message.video.width == message.video.height:
            video = (await bot.download(file=message.video)).read()
            video_note = await message.answer_video_note(video_note=BufferedInputFile(file=video, filename='video_note'))
            text = f'vodeo file_id = {message.video.file_id}\n\nvideo_note file_id = {video_note.video_note.file_id}'

        else:
            text = f'vodeo file_id = {message.video.file_id}'
        
        await message.answer(
            text=text
            )
        
    if message.document:
        print(message.document.file_id) 
        await message.answer(
            text=f'file_id = {message.document.file_id}\n\n'
            )
####################################################


async def main():
    await db.connect()
    await db.create_tables()
    logging.basicConfig(level='INFO')
    await dp.start_polling(bot)


async def close_db():
    await db.close()
        

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(close_db())
        print('STOP')