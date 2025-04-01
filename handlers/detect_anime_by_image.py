import os
import io
import asyncio

import aiohttp

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

from bs4 import BeautifulSoup

from PIL import Image, ImageFilter, ImageDraw, ImageFont

from pysaucenao import errors

from loader import dp, bot, sauce, um
from texts import detect_anime_button
from states import State_DetectAnime
from custom_filters import IsUser



queue = 0

@dp.message(F.text == detect_anime_button, IsUser(),)
async def process_detect_anime_menu(message: Message, state: FSMContext):
    await state.set_state(State_DetectAnime.photo)

    await message.answer(
        text='Отправьте в чат скрин из аниме и бот определит источник 🔗',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❌ Отмена', callback_data='start'),],
        ])
    )

# Принимаем сообщение с фоткой
@dp.message(State_DetectAnime.photo, F.photo, IsUser())
async def process_detect_anime_menu(message: Message, state: FSMContext):
    global queue
    
    await state.clear()
    file = await bot.get_file(message.photo[-1].file_id)
    photo = (await bot.download(file)).read()
    await message.reply('Минутку, начинаю поиск...') 

    loop_requests = 0
    while True:
        if loop_requests >= 3:
            queue -= 1
            if queue < 0: 
                queue = 0
            break

        try:
            if queue <= 3:
                queue += 1
                
                sauce_res = await sauce.from_file(io.BytesIO(photo))
                res = sauce_res.results[0]

                if res.index == 'Anime' or res.index == 'H-Anime':
                    similarity = res.similarity
                    anime_link = res.data['ext_urls'][0]
                    title = res.data['source']
                    episode = res.data['part']
                    year = res.data['year']
                    timestamp = res.data['est_time']

                    pic_data = await get_link_pic(anime_link)
                    pic_result = get_image_amime_info(
                        image_b=pic_data,
                        search_image_b=photo,
                        similarity=str(similarity) + '%',
                        title=title,
                        episode=episode,
                        year=year,
                        timestamp=timestamp
                    )     
                
                await message.answer_photo(
                    photo=BufferedInputFile(file=pic_result, filename='anime'),
                    caption= f'<code>{title}</code>\n',
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='anidb.net', url=anime_link)]
                    ])
                )
                queue -= 1
                if queue < 0: 
                    queue = 0
                break
            
            else:
                await asyncio.sleep(3)
                continue

        except IndexError:
            await message.answer('Ничего не нашел, попробуйте заного')
            loop_requests = 3

        except errors.ShortLimitReachedException and errors.TooManyFailedRequestsException:
            await message.answer('😇 Превышен лимит на запросы, ожидание увеличенно на 30 секунд. Никуда не уходите...')
            await asyncio.sleep(30)
            loop_requests += 1

        except errors.DailyLimitReachedException:
            await message.answer('🖇 Ошибка сервера...')
            await message_for_admins('❗️❗️❗️ Закончились дневные лимиты на поиск аниме')
            loop_requests = 3

        except errors.FileSizeLimitException and errors.ImageSizeException:
            await message.answer('🤗 Вы отправили файл слишком большого или слишком маленького размера, отправьте другой файл заново')
            await state.set_state(State_DetectAnime.photo)
            loop_requests = 3

        except errors.InvalidOrWrongApiKeyException:
            await message.answer('🖇 Ошибка сервера...')
            await message_for_admins('❗️❗️❗️ api ключ неверный')
            loop_requests = 3

        except errors.BannedException:
            await message.answer('🖇 Ошибка сервера...')
            await message_for_admins('❗️❗️❗️ API ЗАБАНЕН ❗️❗️❗️')
            loop_requests = 3
        
        except errors.UnknownStatusCodeException:
            await message.answer('⚙️ Сервис временно недоступен... ')
            await message_for_admins('Внатуре ошибка сервера, скоре всего сервис не доступен')
            loop_requests = 3

        except errors.InvalidImageException:
            await message.answer('😑 Недопустимое изображение')
            await message_for_admins('Недопустимое изображение')
            loop_requests = 3
            
                

# Спарсить обложку аниме
async def get_link_pic(link):
    async with aiohttp.ClientSession(
            headers={'user-agent': 'Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/537.33 (KHTML, like Gecko) Chrome/49.0.3028.293 Safari/603'}
        ) as session:
        
        async with session.get(link) as response:
            html = await response.text()

        soup = BeautifulSoup(html, 'lxml')
        box = soup.find(class_='g_image g_bubble')
        link_pic = box.get('src')

        # Качаем картинку
        async with session.get(link_pic) as response:
            print(response.status)
            if response.status == 200:
                pic_data = await response.read()

    return pic_data


def get_image_amime_info(image_b: bytes, search_image_b: bytes, similarity: str, title: str, episode: str, year: str, timestamp: str):  
    if len(title) > 58:
        cut = title.find(' ', 36)
        new_title_1 = title[:cut] + '\n'
        new_title_2 = title[cut:].strip()
        if len(new_title_2) > 42:
            title = new_title_1 + new_title_2[:42] + '...'
        else:
            title = new_title_1 + new_title_2
    # Формируем строку
    text = title + '\nГод выхода: ' + year + '\nЭпизод: ' + episode + '\nПримерный тайкод: ' + timestamp

    image = Image.open(io.BytesIO(image_b))
    # Для того, чтобы был прозрачный фон
    s_image = Image.open(io.BytesIO(search_image_b))
    search_image = Image.new(mode='RGBA', size=s_image.size, color=(0, 0, 0, 0))
    search_image.paste(s_image, (0, 0))
    # Рабочее изображение
    canvas = Image.new(mode='RGBA', size=(400, 566), color=(0, 0, 0, 0))

    ##################
    # АНИМЕ ОБЛОЖАКА #
    ##################
    width, height = image.size
    if width < height:
        # Изменяем размер сохраняя пропроции
        new_height = 566
        new_width = int(new_height*width/height)
        image = image.resize((new_width, new_height))
    else:
        new_width = 400
        new_height = int(new_width*height/width)
        image = image.resize((new_width, new_height))

    # Расчитываем координаты вставки основного ролика, чтобы картника была по центру
    x_paste = -((new_width-400)/2)
    y_paste = -((new_height-566)/2)
    canvas.paste(image, (int(x_paste), int(y_paste)))

    ###################
    # БЛОК ДЛЯ ТЕКСТА #
    ###################
    s_width, s_height = search_image.size
    if s_width / s_height > 400/220:
        # Изменяем размер по высоте сохраняя пропроции
        new_height = 220
        new_width = int(new_height * s_width / s_height)
        search_image = search_image.resize((new_width, new_height))

    else:
        # Изменяем размер по ширине сохраняя пропроции
        new_width = 450
        new_height = int(new_width * s_height / s_width)
        search_image = search_image.resize((new_width, new_height))

    # Обрезаем картинку по центру
    x1_crop = int((new_width-400)/2)
    y1_crop = int((new_height-220)/2)
    x2_crop = x1_crop + 450
    y2_crop = y1_crop + 220
    search_image = search_image.crop((x1_crop, y1_crop, x2_crop, y2_crop))

    search_image = search_image.filter(ImageFilter.GaussianBlur(5))
    search_image = search_image.rotate(angle=-5, center=(0, 0))
    canvas.paste(im=search_image, box=(0, 346), mask=search_image)

    # Черный экран для затемнения области для текста
    black_screen = Image.new('RGBA', (450, 220), (0, 0, 0, 255))
    black_draw = ImageDraw.Draw(black_screen)
    black_draw.rectangle((0, 0, 450, 220), fill='black')
    black_screen.putalpha(100)
    black_screen = black_screen.rotate(angle=-5, center=(0, 0))
    canvas.paste(im=black_screen, box=(0, 346), mask=black_screen)

    #####################
    # ДОБАВЛЕНИЕ ТЕКСТА #
    #####################
    text_draw = ImageDraw.Draw(canvas)

    font_path = os.path.join('font', 'Nunito.ttf')
    font_percent = ImageFont.truetype(font=font_path, size=40)
    font_title = ImageFont.truetype(font=font_path, size=15)

    text_draw.text(xy=(35, 375), text=similarity, font=font_percent, fill=(84, 255, 224))
    text_draw.text(xy=(35, 430), text=text, font=font_title, fill=(251, 255, 224), spacing=8)

    canvas_byte_arr = io.BytesIO()
    canvas.save(canvas_byte_arr, format='PNG')
    canvas_bytes = canvas_byte_arr.getvalue()

    return canvas_bytes


# Сообщение для всех админов
async def message_for_admins(message: str):
    admins = await um.get_admins(admin=1, main_admin=1)
    for admin in admins:
        await bot.send_message(
            chat_id=admin[0],
            text=message,
        )