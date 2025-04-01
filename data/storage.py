from aiosqlite import connect 

class DatabaseManager: 

    def __init__(self, path):
        self.path = path


    async def connect(self):
        self.conn = await connect(self.path)
        await self.conn.execute('pragma foreign_keys = on')
        await self.conn.commit()
        self.cur = await self.conn.cursor()


    async def query(self, arg, values=None):
        if values is None:
            await self.cur.execute(arg)
        else:
            await self.cur.execute(arg, values)
        await self.conn.commit()
       
        
    async def fetchone(self, arg, values=None):
        if values is None:
            await self.cur.execute(arg)
        else:
            await self.cur.execute(arg, values)

        return await self.cur.fetchone()
    

    async def fetchall(self, arg, values=None):
        if values is None:
            await self.cur.execute(arg)
        else:
            await self.cur.execute(arg, values)

        return await self.cur.fetchall()
    
    
    async def create_tables(self):
        await self.query(
            'CREATE TABLE IF NOT EXISTS all_users (id INTEGER PRIMARY KEY, username TEXT, '
            'first_name TEXT, last_name TEXT, count_anime INTEGER, reg_time DATETIME, status_user TEXT)')
        
        await self.query(
            'CREATE TABLE IF NOT EXISTS anime_quotes (file_unique_id TEXT PRIMARY KEY, file_id TEXT, file_path TEXT,'
            'quote TEXT, anime_title TEXT, time_code TEXT, keys TEXT, type TEXT, user_id INTEGER)')
        
        await self.query(
            'CREATE TABLE IF NOT EXISTS anime_quotes_moder (file_unique_id TEXT PRIMARY KEY, file_id TEXT, file_path TEXT,'
            'quote TEXT, anime_title TEXT, time_code TEXT, keys TEXT, type TEXT, user_id INTEGER)')
        
        await self.query(
            'CREATE TABLE IF NOT EXISTS groups (group_id TEXT PRIMARY KEY, title TEXT, username TEXT, bio TEXT, member_count TEXT)')
    

    async def close(self):
        await self.conn.close()

