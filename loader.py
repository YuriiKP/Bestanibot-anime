import os
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from nltk.stem.snowball import SnowballStemmer

from pysaucenao import SauceNao, AnimeSource, SauceNaoIndexes

from data import DatabaseManager



stemmer = SnowballStemmer('russian')

load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
CHANEL_USERNAME = os.getenv('CHANEL_USERNAME')
SAUCENAOAPI = os.getenv('SAUCENAOAPI')

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
db = DatabaseManager('data/database.db')



#enable or disable indexes
index_hmags='0'
index_reserved='0'
index_hcg='0'
index_ddbobjects='0'
index_ddbsamples='0'
index_pixiv='0'
index_pixivhistorical='0'
index_reserved='0'
index_seigaillust='0'
index_danbooru='0'
index_drawr='0'
index_nijie='0'
index_yandere='0'
index_animeop='0'
index_reserved='0'
index_shutterstock='0'
index_fakku='0'
index_hmisc='0'
index_2dmarket='0'
index_medibang='0'
index_anime='1'
index_hanime='1'
index_movies='0'
index_shows='0'
index_gelbooru='0'
index_konachan='0'
index_sankaku='0'
index_animepictures='0'
index_e621='0'
index_idolcomplex='0'
index_bcyillust='0'
index_bcycosplay='0'
index_portalgraphics='0'
index_da='0'
index_pawoo='0'
index_madokami='0'
index_mangadex='0'

#generate appropriate bitmask
db_bitmask = int(index_mangadex+index_madokami+index_pawoo+index_da+index_portalgraphics+index_bcycosplay+index_bcyillust+index_idolcomplex+index_e621+index_animepictures+index_sankaku+index_konachan+index_gelbooru+index_shows+index_movies+index_hanime+index_anime+index_medibang+index_2dmarket+index_hmisc+index_fakku+index_shutterstock+index_reserved+index_animeop+index_yandere+index_nijie+index_drawr+index_danbooru+index_seigaillust+index_anime+index_pixivhistorical+index_pixiv+index_ddbsamples+index_ddbobjects+index_hcg+index_hanime+index_hmags, 2)

# sauce = SauceNao(
#     api_key=SAUCENAOAPI,
#     db_mask=db_bitmask,
#     results_limit=3,
# )

indexes = SauceNaoIndexes().add(SauceNaoIndexes.ANIME).add(SauceNaoIndexes.H_ANIME)

sauce = SauceNao(
    api_key=SAUCENAOAPI,
    indexes=indexes,
    max_results=3,
)



deep_links_admin_manage = {}

symbols = (
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', 
    '2', '3', '4', '5', '6', '7', '8', '9'
)


class UsersManager:
    async def add_new_user(self, id, username, first_name, last_name):
        '''Сохранить нового пользователя в базу'''

        await db.query(
            'INSERT OR IGNORE INTO all_users VALUES (?, ?, ?, ?, ?, ?, ?)', 
            id, username, first_name, last_name, 0, datetime.now(), 'user'
        )


    async def get_user(self, id):
        '''Получить информацию о пользователе из базы'''
        return await db.fetchone('SELECT * FROM all_users WHERE id = ?', (id,))


    async def get_users(self) -> list:
        '''Получить всех пользователей из базы'''
        return await db.fetchall('SELECT * FROM all_users')
    

    async def get_users_id(self) -> list:
        '''Получить ид всех пользователей из базы'''
        return [user_id[0] for user_id in await db.fetchall('SELECT id FROM all_users')]
    

    async def get_admins(self, moder: bool = None, admin: bool = None, main_admin: bool = None):
        '''Получить список администраторов'''
        if moder:
            moder = 'moder'
        if admin:
            admin = 'admin'
        if main_admin:
            main_admin = 'main_admin'

        return await db.fetchall(
                'SELECT * FROM all_users WHERE status_user = ? OR status_user = ? OR status_user = ?',
                (moder, admin, main_admin)
            )


    async def update_user(self, id: str, username: str = None, first_name: str = None, last_name: str = None, count_anime: int = None, reg_time=None, status_user=None):
        '''
        Обновить информацию о пользователе.
        Значение в count_anime прибавляется к значению в базе
        '''

        user = await self.get_user(id)

        if username is None:
            username = user[1]
        
        if first_name is None:
            first_name = user[2]
        
        if last_name is None:
            last_name = user[3]
        
        if count_anime is None:
            count_anime = user[4]
        else:
            count_anime_old = user[4]
            count_anime = int(count_anime) + int(count_anime_old)

        if reg_time is None:
            reg_time = user[5]

        if status_user is None:
            status_user = user[6]

        await db.query(
            'UPDATE all_users SET username = ?, first_name = ?, last_name = ?, count_anime = ?, reg_time = ?, status_user = ? WHERE id = ?', 
            (username, first_name, last_name, count_anime, reg_time, status_user, id)
        )




class AnimeManager:
    async def add_amine_qoute(self, file_unique_id: str, file_id: str, file_path: str, quote: str, anime_title: str, time_code: str, keys: str, type: str, user_id: int) -> None:
        '''Сохнанить новую цитату из аниме'''

        if keys:
            if keys[-1] == ',':
                keys = keys[:-1]

        new_keys = ', '.join((quote.strip(), anime_title.strip(), keys.strip()))
        new_keys = new_keys.lower()

        await db.query(
            'INSERT OR REPLACE INTO anime_quotes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
            (file_unique_id, file_id, file_path, quote.lower(), anime_title, time_code, new_keys, type, user_id)
        )


    async def update_amine_qoute(
            self, 
            file_unique_id: str,
            file_unique_id_2: str = None, 
            file_id: str = None, 
            file_path: str = None, 
            quote: str = None, 
            anime_title: str = None, 
            time_code: str = None, 
            keys: str = None, 
            type: str = None, 
            user_id: int = None
        ) -> None:
        '''Отредактировать цитату'''

        quote_info = await self.get_anime_quote_by_id(file_unique_id)

        if file_unique_id_2 is None:
            file_unique_id_2 = file_unique_id

        if file_id is None:
            file_id = quote_info[1]
        if file_path is None:
            file_path = quote_info[2]
        if quote is None:
            quote = quote_info[3]
        if anime_title is None:
            anime_title = quote_info[4]
        if time_code is None:
            time_code = quote_info[5]
        if keys is None:
            keys = quote_info[6]
        if type is None:
            type = quote_info[7]
        if user_id is None:
            user_id = quote_info[8]

        await db.query(
            'UPDATE anime_quotes SET file_unique_id = ?, file_id = ?, file_path = ?, quote = ?, anime_title = ?, time_code = ?, keys = ?, type = ?, user_id = ? WHERE file_unique_id = ?',
            (file_unique_id_2, file_id, file_path, quote, anime_title, time_code, keys, type, user_id, file_unique_id)
        )


    async def add_amine_qoute_moder(self, file_unique_id: str, file_id: str, file_path: str, quote: str, anime_title: str, time_code: str, keys: str, type: str, user_id: int) -> None:
        '''Отправить цитату на модерацию'''

        if keys:
            if keys[-1] == ',':
                keys = keys[:-1]

        new_keys = ', '.join((quote.strip(), anime_title.strip(), keys.strip()))
        new_keys = new_keys.lower()

        await db.query(
            'INSERT OR REPLACE INTO anime_quotes_moder VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
            (file_unique_id, file_id, file_path, quote, anime_title, time_code, new_keys, type, user_id)
        )

    
    async def update_amine_qoute_moder(
            self, 
            file_unique_id: str,
            file_unique_id_2: str = None, 
            file_id: str = None, 
            quote: str = None, 
            anime_title: str = None, 
            time_code: str = None, 
            keys: str = None, 
            type: str = None, 
            user_id: int = None
        ) -> None:
        '''Отредактировать цитату на модерации'''

        quote_info = await self.get_anime_quote_moder_by_id(file_unique_id)

        if file_unique_id_2 is None:
            file_unique_id_2 = file_unique_id

        if file_id is None:
            file_id = quote_info[1]
        if quote is None:
            quote = quote_info[3]
        if anime_title is None:
            anime_title = quote_info[4]
        if time_code is None:
            time_code = quote_info[5]
        if keys is None:
            keys = quote_info[6]
        if type is None:
            type = quote_info[7]
        if user_id is None:
            user_id = quote_info[8]

        new_file_path = os.path.join('data', 'video', f'{quote} {anime_title} {time_code}.mp4')

        await db.query(
            'UPDATE anime_quotes_moder SET file_unique_id = ?, file_id = ?, file_path = ?, quote = ?, anime_title = ?, time_code = ?, keys = ?, type = ?, user_id = ? WHERE file_unique_id = ?',
            (file_unique_id_2, file_id, new_file_path, quote, anime_title, time_code, keys, type, user_id, file_unique_id)
        )


    async def get_anime_quotes(self, query: str, offset:int) -> list:
        '''Возвращает цитаты по запросу'''

        limit = offset * 50
        if query:
            stemmed_query = stemmer.stem(query) # Стемминг запроса для поиска

            results: list = await db.fetchall('SELECT * FROM anime_quotes WHERE quote = ?', (query,))
            results.extend(
                await db.fetchall(
                    'SELECT * FROM anime_quotes WHERE keys LIKE ? AND file_unique_id NOT IN (SELECT file_unique_id FROM anime_quotes WHERE quote = ?) LIMIT ?', 
                    (f'%{stemmed_query}%', query, limit)
                )
            )
            results = results[limit - 50:]

            return results
        else:
            return []
        

    async def get_anime_quotes_type(self, query_type: str, offset:int) -> list:
        '''Возвращает все цитаты по типу'''
        
        limit = offset * 50
        if query_type:
            results = await db.fetchall('SELECT * FROM anime_quotes WHERE type = ? LIMIT ?', (query_type, limit,))
            
            results = results[limit - 50:]

            return results
        else:
            return []


    async def get_anime_quote_by_id(self, file_unique_id: str) -> list:
        '''Получить цитату по уникальному ид'''

        return await db.fetchone('SELECT * FROM anime_quotes WHERE file_unique_id = ?', (file_unique_id,)) 


    async def all_anime_quotes(self) -> list:
        '''Получить все цитаты в базе'''
        return await db.fetchall('SELECT * FROM anime_quotes')

       
    async def random_anime_quote(self) -> tuple:
        '''Возвращает случайную цитату'''
        return await db.fetchone('SELECT * FROM anime_quotes ORDER BY RANDOM() LIMIT 1')
    

    async def count_anime_quote(self) -> int:
        '''Получить кол-во цитат'''
        count = (await db.fetchone('SELECT COUNT(*) FROM anime_quotes'))[0]
        return int(count)


    async def get_anime_quote_moder_by_id(self, file_unique_id: str) -> list:
        '''Получить цитату по уникальному ид из модерации'''

        return await db.fetchone('SELECT * FROM anime_quotes_moder WHERE file_unique_id = ?', (file_unique_id,))
    

    async def get_anime_quotes_moder(self) -> list:
        '''Получить цитату по уникальному ид из модерации'''

        return await db.fetchall('SELECT * FROM anime_quotes_moder')
    

    async def del_anime_quote_moder_by_id(self, file_unique_id: str) -> None:
        '''Удалить цитату из модерации'''

        await db.query('DELETE FROM anime_quotes_moder WHERE file_unique_id = ?', (file_unique_id,))


    async def del_all_anime_quote_moder(self, user_id: str) -> None:
        '''Удалить все цитаты пользователя с проверки'''

        await db.query('DELETE FROM anime_quotes_moder WHERE user_id = ?', (user_id,))



class GroupsManager():
    async def add_group(self, group_id:str, title:str, username:str, bio:str, member_count:str) -> None:
        '''Сохранить группу в базе'''

        await db.query(
            'INSERT OR REPLACE INTO groups VALUES (?, ?, ?, ?, ?)',
            (group_id, title, username, bio, member_count)
            )


am = AnimeManager()
um = UsersManager()
gm = GroupsManager()