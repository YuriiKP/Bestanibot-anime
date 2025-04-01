from aiogram import F
from aiogram.types import InlineQuery
from aiogram.types import InlineQueryResultCachedVideo

from loader import dp, am


# Обработка поиска
@dp.inline_query(F.query.not_contains('/'))
async def show_quotes(inline_query: InlineQuery):
    if inline_query.offset:
        offset = int(inline_query.offset)
    else:
        offset = 1
    
    results_query = await am.get_anime_quotes(inline_query.query, offset)

    results = []
    for result in results_query:
        video = InlineQueryResultCachedVideo(
            id=result[0],
            video_file_id=result[1],
            title=result[3],
            description=f'{result[4]} {result[5]}',

        )
        
        results.append(video)  

    await inline_query.answer(
        cache_time=86400,
        results=results,
        is_personal=False,
        next_offset=str(offset + 1),
    )


# Обработка цитат по типу
@dp.inline_query(F.query.contains('/'))
async def show_quotes_by_type(inline_query: InlineQuery):
    if inline_query.offset:
        offset = int(inline_query.offset)
    else:
        offset = 1
    
    if inline_query.query == '/радость':
        results_query = await am.get_anime_quotes_type('радость', offset)

    elif inline_query.query == '/грусть':
        results_query = await am.get_anime_quotes_type('грусть', offset)

    elif inline_query.query == '/любовь':
        results_query = await am.get_anime_quotes_type('любовь', offset)

    elif inline_query.query == '/прощание':
        results_query = await am.get_anime_quotes_type('прощание', offset)

    elif inline_query.query == '/приветствие':
        results_query = await am.get_anime_quotes_type('приветствие', offset)

    elif inline_query.query == '/отрицание':
        results_query = await am.get_anime_quotes_type('отрицание', offset)

    elif inline_query.query == '/согласие':
        results_query = await am.get_anime_quotes_type('согласие', offset)

    elif inline_query.query == '/злость':
        results_query = await am.get_anime_quotes_type('злость', offset)

    elif inline_query.query == '/ругать':
        results_query = await am.get_anime_quotes_type('ругать', offset)

    elif inline_query.query == '/хвалить':
        results_query = await am.get_anime_quotes_type('хвалить', offset)

    else:
        results_query = []

    results = []
    for result in results_query:
        video = InlineQueryResultCachedVideo(
            id=result[0],
            video_file_id=result[1],
            title=result[3],
            description=f'{result[4]} {result[5]}'
        )
        
        results.append(video)

    await inline_query.answer(
        results=results,
        is_personal=False,
        next_offset=str(offset + 1),
    )