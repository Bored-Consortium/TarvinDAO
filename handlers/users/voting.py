from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardRemove

from sqlite_conection import SqliteConnection

from loader import dp
from aiogram import types
from states import CallbackCreateVoting


@dp.message_handler(Command('createvoting'))
async def start_create_voting(message: types.Message):
    connection = SqliteConnection()
    user = connection.get_user(message.from_user.id)
    if not user:
        await message.answer("Для того, чтобы голосование, необходимо зарегистрироваться")
    elif user == "Ошибка":
        await message.answer("Пользователь не найден, проверьте свою регистрацию")
    else:
        result = connection.check_admin(message.from_user.id)
        connection.close()
        if result not in (0, 1):
            await message.answer(result)
        elif result:
            await message.answer("Опишите проблему", reply_markup=ReplyKeyboardRemove())
            await CallbackCreateVoting.Q1.set()
        else:
            await message.answer("Вы должны зайти под администратором, чтобы создать голосование")


@dp.message_handler(state=CallbackCreateVoting.Q1)
async def bottom_threshold_create(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите количество токенов, необходимых для получения права голосования")
    await CallbackCreateVoting.next()


@dp.message_handler(state=CallbackCreateVoting.Q2)
async def upside_threshold_create(message: types.Message, state: FSMContext):
    await state.update_data(bottom_threshold=message.text)
    await message.answer("Введите количество токенов, необходимых для того, чтобы голосование считалось действительным")
    await CallbackCreateVoting.next()


@dp.message_handler(state=CallbackCreateVoting.Q3)
async def end_creating(message: types.Message, state: FSMContext):
    await state.update_data(upside_threshold=message.text)
    data = await state.get_data()
    connection = SqliteConnection()
    result = connection.add_voting(data["bottom_threshold"], data["upside_threshold"], data["description"])
    if result is None:
        await message.answer("Голосование успешно создано")
    else:
        await message.answer(result)
    connection.close()
    await state.finish()

