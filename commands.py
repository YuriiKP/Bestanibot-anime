from aiogram.types import BotCommand



user_commands=[
    BotCommand(command='start', description='Перезапустить бота'),
    BotCommand(command='rand', description='Рандомная фраза'),
    BotCommand(command='help', description='Инфо'),
    ]


chat_commands=[
    BotCommand(command='rand', description='Рандомная фраза'),
    BotCommand(command='quote', description='(отправлять в ответ на сообщение) Фраза на текст в сообщении')
    ]