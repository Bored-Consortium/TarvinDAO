from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку",
            "/admin - Войти под администратором",
            "/registeruser - Зарегистрироваться в системе",
            "/myprofile - Посмотреть профиль",
            "/createvoting - Создать голосование",
            "/listvotings - Просмотр текущих голосований")

    await message.answer("\n".join(text))
