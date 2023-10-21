from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext

import utils.stats
from sqlite_conection import SqliteConnection
from keyboards.inline.confirm import confirm

from loader import dp
from aiogram import types
from states import CallbackBecomeAdmin, CallbackRegisterUser


@dp.message_handler(Command('registeruser'))
async def register_user(message: types.Message):
    connection = SqliteConnection()
    result = connection.check_user(message.from_user.id)
    connection.close()
    if result:
        await message.answer("Такой пользователь уже есть")
    else:
        await message.answer("Пришлите свой TON кошелек")
        await CallbackRegisterUser.Q1.set()


@dp.message_handler(state=CallbackRegisterUser.Q1)
async def ton_purse_register(message: types.Message, state: FSMContext):
    await state.update_data(ton=message.text)
    await state.update_data(username=message.from_user.username)
    await state.update_data(id=message.from_user.id)
    await message.answer(f"Вы подтвержаете, что кошелек https://tonscan.org/address/{message.text} принадлежит вам?",
                         reply_markup=confirm())
    await CallbackRegisterUser.next()


@dp.callback_query_handler(state=CallbackRegisterUser.Q2)
async def end_register(call: types.CallbackQuery, state: FSMContext):
    if call.data == "Да":
        data = await state.get_data()
        connection = SqliteConnection()
        result = connection.add_user(data["id"], data["username"], data["ton"])
        if result is None:
            await call.message.answer(f"Пользователь {data['username']} успешно добавлен")
        else:
            await call.message.answer(result)
        connection.close()
    else:
        await call.message.answer("Регистрация отменена")
    await state.finish()


@dp.message_handler(Command('myprofile'))
async def profile_user(message: types.Message):
    connection = SqliteConnection()
    result = connection.get_user(message.from_user.id)
    if result is None:
        await message.answer("Пользователь не найден")
    elif result == "Ошибка":
        await message.answer(result)
    else:
        result = list(map(str, result))
        column = ['ID', 'username', 'voting tokens', 'reward tokens']
        await message.answer('\n'.join(map(lambda x: column[x] + ': ' + result[x], range(4))))


@dp.message_handler(Command('admin'))
async def become_admin(message: types.Message):
    connection = SqliteConnection()
    result = connection.check_admin(message.from_user.id)
    connection.close()
    if result not in (0, 1):
        await message.answer(result)
    elif result:
        await message.answer('Вы уже вошли как админ')
    else:
        await message.answer('Введите пароль')
        await CallbackBecomeAdmin.Q1.set()


@dp.message_handler(state=CallbackBecomeAdmin.Q1)
async def check_admin_password(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == utils.stats.admin_password:
        connection = SqliteConnection()
        result = connection.create_admin(message.from_user.id)
        if result is None:
            await message.answer("Вы зашли под администратором")
        else:
            await message.answer(result)
        connection.close()
    else:
        await message.answer("Неправильный пароль")
    await state.finish()
