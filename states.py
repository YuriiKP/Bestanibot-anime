from aiogram.fsm.state import StatesGroup, State


class State_add_quote(StatesGroup):
    video_file = State()
    quote = State()
    anime_title = State()
    time_code = State()
    keys = State()
    type = State()


class State_check_true_msg(StatesGroup):
    msg = State()


class State_check_false_msg(StatesGroup):
    msg = State()


class State_edit_quote_moder(StatesGroup):
    video_file = State()
    quote = State()
    anime_title = State()
    time_code = State()
    keys = State()
    type = State()


class State_Ban_Admin(StatesGroup):
    msg = State()


class State_Mailing(StatesGroup):
    msg = State()
    add_button = State()


class State_Edit_Amine_Quotes(StatesGroup):
    settings_quote = State()
    video = State()
    quote_info = State()
    select_quote = State()


class State_DetectAnime(StatesGroup):
    photo = State()