from aiogram.filters import Filter
from aiogram.types import Message

from loader import um



class IsMainAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user_info = await um.get_user(user_id)
        return user_info[6] == 'main_admin'
    

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user_info = await um.get_user(user_id)
        return user_info[6] == 'admin' or user_info[6] == 'main_admin'
    

class IsModer(Filter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user_info = await um.get_user(user_id)
        return user_info[6] == 'moder' or user_info[6] == 'admin' or user_info[6] == 'main_admin'
    

class IsUser(Filter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user_info = await um.get_user(user_id)
        print(user_info)
        return user_info[6] == 'user' or user_info[6] == 'moder' or user_info[6] == 'admin' or user_info[6] == 'main_admin'
    

class IsPidor(Filter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user_info = await um.get_user(user_id)
        return user_info[6] == 'pidor'