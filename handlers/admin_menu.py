import os
from random import randint
import asyncio

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramForbiddenError

from loader import dp, bot, am, um, deep_links_admin_manage, symbols, ADMIN_ID
from texts import about_users_bot, add_admin
from states import State_Ban_Admin, State_Mailing
from keyboards import select_type_quote
from custom_callbackdata import CB_ModerAdmins
from custom_filters import IsMainAdmin


# Показать кол-во юзеров
@dp.message(F.text == about_users_bot, IsMainAdmin())
async def show_info_about_users_bot(message: Message, state: FSMContext):
    await state.clear()

    all_users = await um.get_users_id()

    text = f'<b>👥 ПОЛЬЗОВАТЕЛИ</b>\n{len(all_users)}'

    await message.answer(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='📨 Сделать рассылку', callback_data='mailing')]
        ])
    )

# Настройка рассылки 
@dp.callback_query(F.data == 'mailing', IsMainAdmin())
async def setting_mailing(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_Mailing.msg)
    
    await query.message.answer(
        text='Отправьте или перешлите сообщение для рассылки:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❌ Отмена', callback_data='stop_mailing')]
        ])
    )

# Отмена рассылки
@dp.callback_query(F.data == 'stop_mailing', IsMainAdmin())
async def stop_mailing(query: CallbackQuery, state: FSMContext):
    await show_info_about_users_bot(query.message, state)


# Получение сообщения для расылки
@dp.message(State_Mailing.msg, IsMainAdmin())
async def take_msg_mailing(message: Message, state: FSMContext):
    users = await um.get_users_id()
    text_buttons = []
    urls = []
    
    # Создаем кнопки
    async def bulding_keyboard():
        builder = InlineKeyboardBuilder()
        
        if text_buttons:
            for text_button, url in zip(text_buttons, urls):
                builder.button(text=text_button, url=url)
        
        builder.button(text='▶️ Добавить кнопку', callback_data='add_button')
        builder.button(text='📤 Начать рассылку', callback_data='confirm_start_mailing')
        builder.button(text='❌ Отмена', callback_data='stop_mailing')

        builder.adjust(1)

        return builder.as_markup()

    # Отправляем сообщение с настройкой рассылки в чат
    async def send_settings_mailing(keyboard):
        await bot.copy_message(
            chat_id=message.from_user.id,
            from_chat_id=message.from_user.id,
            message_id=message.message_id,
            reply_markup=keyboard
        )

    keyboard = await bulding_keyboard()
    await send_settings_mailing(keyboard)


    # Добавление кнопки
    @dp.callback_query(F.data == 'add_button', IsMainAdmin())
    async def add_button(query: CallbackQuery, state: FSMContext):
        await state.set_state(State_Mailing.add_button)
        
        await query.message.answer(
            text='Введите текст кнопки и ссылку в формате:\nТекст кнопки - https://example'
        )


    # Принимаем сообщение для кнопки
    @dp.message(State_Mailing.add_button, IsMainAdmin())
    async def take_button_text(message: Message, state: FSMContext):
        raw_text = message.text.split('-')
        button_text = raw_text[0].strip()
        url = raw_text[1].strip()

        text_buttons.append(button_text)
        urls.append(url)

        keyboard = await bulding_keyboard()
        await send_settings_mailing(keyboard)

    
    # Подтверждение рассылки
    @dp.callback_query(F.data == 'confirm_start_mailing', IsMainAdmin())
    async def confirm_start_mailing(query: CallbackQuery, state: FSMContext):
        await query.message.answer(
            text=f'Начать рассылку?\n\nРасчетное время рассылки: {round(len(users)*0.05, 0)}',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='✅ Начать', callback_data='start_mailing')],
                [InlineKeyboardButton(text='❌ Отмена', callback_data='stop_mailing')]
            ])
        )

    # Начинаем рассылку
    @dp.callback_query(F.data == 'start_mailing', IsMainAdmin())
    async def start_mailing(query: CallbackQuery, state: FSMContext):
        builder = InlineKeyboardBuilder()
        if text_buttons:
            for text_button, url in zip(text_buttons, urls):
                builder.button(text=text_button, url=url)
            builder.adjust(1)
        
        # Для расчета прогресса
        ind = round(len(users)/5, 0)
        if ind == 0:
            ind = 1


        count_msg = []
        for index, user  in enumerate(users):
            if index % ind == 0:
                await message.answer(text=f'Прогресс рассылки {int(index/ind*20)}%')

            # Обработка отправки
            async def send_msg():
                try:
                    await bot.copy_message(
                        chat_id=user,
                        from_chat_id=message.from_user.id,
                        message_id=message.message_id,
                        reply_markup=builder.as_markup()
                    )
                    
                    count_msg.append(1)
                    print(f'Отправил сообщение {index + 1}')
                
                except TelegramRetryAfter as e:
                    print('Ошбика попробую через', e.retry_after)
                    await asyncio.sleep(e.retry_after)
                    await send_msg()
                
                except TelegramBadRequest as e:
                    print(e)
                
                except TelegramForbiddenError as e:
                    print(e)

            await send_msg()
            await asyncio.sleep(1/20)

        count_msg_len = len(count_msg)
        await message.answer(
            text=f'<b>РАССЫЛКА ЗАВЕРШЕНА</b>\n\nВсего пользователей: {len(users)}\nУспешно отправленно: {count_msg_len}\nНе удалось отправить: {len(users)-count_msg_len}'
        )


################################################################################
# Управление админами
@dp.message(F.text == add_admin, IsMainAdmin())
async def admin_manage_menu(message: Message, state: FSMContext):
    await state.clear()

    admins = await um.get_admins(moder=1, admin=1, main_admin=1)

    text = '<b>ВСЕ АДМИНИСТРАТОРЫ</b>'
    for admin in admins:
        if int(admin[0]) == int(ADMIN_ID):
            pass
        else:
            text += f'\n\n{admin[6]} <a href="tg://user?id={admin[0]}">{admin[2]}</a> ID: {admin[0]}'

    await message.answer(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🛠 Добавить админа', callback_data='add_admin')],
            [InlineKeyboardButton(text='🍌 Разжаловать', callback_data='ban_admin')],
        ])
    )

# Кого добавить
@dp.callback_query(F.data == 'add_admin', IsMainAdmin())
async def choice_add_admin(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        text='Кого добавляем?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Главного админа', callback_data=CB_ModerAdmins(action='add_admin', status_user='main_admin').pack())],
            [InlineKeyboardButton(text='Админа', callback_data=CB_ModerAdmins(action='add_admin', status_user='admin').pack())],
            [InlineKeyboardButton(text='Модератора', callback_data=CB_ModerAdmins(action='add_admin', status_user='moder').pack())],
        ])
    )

# Создание ссылки
@dp.callback_query(CB_ModerAdmins.filter(F.action == 'add_admin'), IsMainAdmin())
async def prpcess_add_admin(query: CallbackQuery, state: FSMContext, callback_data: CB_ModerAdmins):
    status_user = callback_data.status_user
    
    str_link = ''
    for _ in range(5):
        str_link += symbols[randint(0, 35)]
        
    start_link = await create_start_link(
        bot = bot,
        payload=str_link
    )
    
    deep_links_admin_manage[str_link] = status_user

    await query.message.answer(
        text=start_link
    )


# Удаление админа
@dp.callback_query(F.data == 'ban_admin', IsMainAdmin())
async def process_ban_admin(query: CallbackQuery, state: FSMContext):
    await state.set_state(State_Ban_Admin.msg)

    await query.message.answer(
        text='Отправьте id пользователя'
    )

# Полчение ид пользователя
@dp.message(State_Ban_Admin.msg, IsMainAdmin())
async def ban_admin(message: Message, state: FSMContext):   
    try:
        await um.update_user(
            id=message.text,
            status_user='user'
        )

        await message.answer(
            text=f'Пользователь {message.text} удален из админов'
        )

        await state.clear()
    
    except TypeError:
        await message.answer(
            text=f'Такого пользователя нет, отправьте id заново'
        )