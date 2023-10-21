from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardRemove

from sqlite_conection import SqliteConnection
from keyboards.inline.confirm import confirm

from loader import dp
from aiogram import types
from states import CallbackCreateVoting
from requests import get


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
    if result != "Ошибка":
        await message.answer("Голосование успешно создано")
    else:
        await message.answer(result)
        connection.close()
        await state.finish()
        return

    users_id = connection.get_users_id()
    voting_id = connection.get_last_id_voting_from_description(data["description"])

    if users_id == "Ошибка" or voting_id == "Ошибка":
        await message.answer("Не удалось отправить голосование пользователям")
    else:
        for user_id in users_id:
            msg = await dp.bot.send_message(user_id[0], data["description"], reply_markup=confirm())
            connection.create_message_vote(msg.message_id, voting_id, user_id[0])
        await message.answer("Голосование успешно отправлено всем пользователям")

    connection.close()
    await state.finish()


@dp.callback_query_handler(lambda c: check_message_vote(c.message.message_id))
async def make_election(call: types.CallbackQuery):
    connection = SqliteConnection()
    message_vote = connection.get_message_vote(call.message.message_id)
    vote = connection.get_vote(message_vote[2], message_vote[1])
    user = connection.get_user(message_vote[2])
    voting = connection.get_voting(message_vote[1])

    if user == "Ошибка" or voting == "Ошибка":
        await call.message.answer(user)
        connection.close()
        return

    url = f"https://tonapi.io/v2/accounts/{user[5]}"
    answer = get(url).json()
    balance = answer["balance"] // 10 ** 9

    if vote is not None and vote != "Ошибка":
        await dp.bot.answer_callback_query(callback_query_id=call.id, text="Вы уже проголосовали", show_alert=True)
        connection.close()
        return
    connection.change_balance(user[0], balance)
    if balance < voting[7]:
        await dp.bot.answer_callback_query(callback_query_id=call.id, text="У вас недостаточно токенов", show_alert=True)
        connection.close()
        return
    if voting[1] + voting[3] >= voting[6]:
        await dp.bot.answer_callback_query(callback_query_id=call.id, text="Голосование закончилось", show_alert=True)
        connection.close()
        return
    result = connection.add_vote(user[0], voting[0], balance, 1 if call.data == "Да" else 0)
    if result != "Ошибка":
        await dp.bot.answer_callback_query(callback_query_id=call.id, text="Ваш ответ записан", show_alert=True)

    if balance + voting[1] + voting[3] >= voting[6]:
        users = connection.get_users_id()
        if users == "Ошибка":
            connection.close()
            return
        for item in users:
            await dp.bot.send_message(item[0],
                                      f"Голосование '{voting[5]}' закончилось.\nРезультаты:\n'Да': {voting[1] + balance * (1 if call.data == 'Да' else 0)}\n'Нет': {voting[3] + balance * (0 if call.data == 'Да' else 1)}", reply_markup=ReplyKeyboardRemove())

    connection.close()


def get_current_voting_descriptions():
    connection = SqliteConnection()
    result = connection.get_current_voting_description()
    connection.close()
    return list(map(lambda x: x[0], result)) if result != "Ошибка" else []


def check_message_vote(message_id):
    connection = SqliteConnection()
    result = connection.get_message_vote(message_id)
    connection.close()
    return True if result != "Ошибка" and result is not None else False


@dp.message_handler(Command("listvotings"))
async def view_list(message: types.Message):
    connection = SqliteConnection()
    user = connection.get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала зарегистрируйтесь")
    elif user == "Ошибка":
        await message.answer(user)
    else:
        result = connection.get_all_votings()
        if result == "Ошибка":
            await message.answer(result)
        else:
            for voting in result:
                msg = await dp.bot.send_message(message.from_user.id, voting[5], reply_markup=confirm())
                connection.create_message_vote(msg.message_id, voting[0], message.from_user.id)
    connection.close()


