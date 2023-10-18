from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlite_conection import SqliteConnection


def params():
    connection = SqliteConnection()
    answer = list(map(lambda x: x[0], connection.get_params()))
    param = []
    for i in range(0, len(answer), 3):
        param.append(answer[i:i+3])
    if len(answer) % 3:
        param.append(answer[-(len(answer) % 3):])

    button_list = []
    for item in param:
        tmp = []
        for i in item:
            tmp.append(InlineKeyboardButton(text=i, callback_data=i))
        button_list.append(tmp)

    keyword_inline_buttons = InlineKeyboardMarkup(inline_keyboard=button_list)
    connection.close()
    return keyword_inline_buttons

