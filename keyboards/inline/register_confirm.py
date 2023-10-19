from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def register_confirm():
    button_list = [[InlineKeyboardButton(text="Да", callback_data="Да"),
                   InlineKeyboardButton(text="Нет", callback_data="Нет")]]
    keyword_inline_buttons = InlineKeyboardMarkup(inline_keyboard=button_list)
    return keyword_inline_buttons
