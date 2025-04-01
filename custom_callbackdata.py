from aiogram.filters.callback_data import CallbackData



class CallbackData_CheckQuote(CallbackData, prefix='check_quote'):
    action: str
    file_unique_id: str


class CB_ModerAdmins(CallbackData, prefix='moder_admins'):
    action: str
    status_user: str