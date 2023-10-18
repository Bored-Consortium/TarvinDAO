from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardRemove

from keyboards.inline.choice_param import params
from keyboards.inline.choice_kvorum import type_kvorum
from keyboards.inline.choice_agreement import type_agreement
from keyboards.inline.choice_function import type_function
from keyboards.inline.choice_reward import type_reward
from keyboards.inline.choice_duration import type_duration
from sqlite_conection import SqliteConnection

from loader import dp
from aiogram import types
from states import CallbackCreateVotingOnParam


@dp.message_handler(Command('createvotingparam'))
async def start_create(message: types.Message):
    connection = SqliteConnection()
    user = connection.get_user(message.from_user.id)
    connection.close()
    if not user:
        await message.answer("Для того, чтобы создать голосование, необходимо зарегистрироваться")
    elif user == "Ошибка":
        await message.answer("Пользователь не найден, проверьте свою регистрацию")
    else:
        await message.answer("Опишите проблему", reply_markup=ReplyKeyboardRemove())
        await CallbackCreateVotingOnParam.Q1.set()


@dp.message_handler(state=CallbackCreateVotingOnParam.Q1)
async def change_param(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(description=answer)
    await message.answer("Выберите параметр", reply_markup=params())
    await CallbackCreateVotingOnParam.next()


@dp.callback_query_handler(state=CallbackCreateVotingOnParam.Q2)
async def change_type(call, state: FSMContext):
    answer = call.data
    await state.update_data(param=answer)
    if answer == "kvorum":
        await call.message.answer("Выберите новый тип", reply_markup=type_kvorum())
    elif answer == "agreement":
        await call.message.answer("Выберите новый тип", reply_markup=type_agreement())
    elif answer == "function":
        await call.message.answer("Выберите новый тип", reply_markup=type_function())
    elif answer == "reward":
        await call.message.answer("Выберите новый тип", reply_markup=type_reward())
    elif answer == "duration":
        await call.message.answer("Выберите новый тип", reply_markup=type_duration())
    await CallbackCreateVotingOnParam.next()


@dp.callback_query_handler(state=CallbackCreateVotingOnParam.Q3)
async def change_value(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await call.message.answer("Введите новое значение", reply_markup=ReplyKeyboardRemove())
    await CallbackCreateVotingOnParam.next()


@dp.message_handler(state=CallbackCreateVotingOnParam.Q4)
async def end_create(message: types.Message, state: FSMContext):
    await state.update_data(value=message.text)
    data = await state.get_data()
    connection = SqliteConnection()
    result = connection.add_voting(90, data['param'], data['type'], data['value'], data['description'])
    if result is None:
        await message.answer("Голосование успешно созданно")
    else:
        await message.answer(result)
    connection.close()
    await state.finish()




