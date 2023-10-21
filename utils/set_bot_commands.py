from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Вывести справку"),
        types.BotCommand("registeruser", "Зарегистрироваться в системе"),
        types.BotCommand("admin", "Войти как админ"),
        types.BotCommand("myprofile", "Посмотреть профиль"),
        types.BotCommand("createvoting", "Создать голосование"),
        types.BotCommand("listvotings", "Просмотр текущих голосований")
    ])
