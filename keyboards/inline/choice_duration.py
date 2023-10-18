from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def type_duration():
    list_button_name = [['days', 'weeks']]

    button_list = []
    for item in list_button_name:
        tmp = []
        for i in item:
            tmp.append(InlineKeyboardButton(text=i, callback_data=i))
        button_list.append(tmp)

    keyword_inline_buttons = InlineKeyboardMarkup(inline_keyboard=button_list)
    return keyword_inline_buttons
