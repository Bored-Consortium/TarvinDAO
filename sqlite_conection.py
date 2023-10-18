import sqlite3
from get_time import get_end_time


class SqliteConnection:
    def __init__(self):
        self.connection = sqlite3.connect('data/information.db')
        self.cursor = self.connection.cursor()

    def add_user(self, user_id, nickname):
        try:
            result = self.cursor.execute("""SELECT id_user FROM users
                                            WHERE id_user = ?""", (user_id,)).fetchone()
            if result:
                return "Такой пользователь уже есть"
            self.cursor.execute("""INSERT INTO users (id_user, username, tokens_voting, tokens_reward) 
                                    VALUES (?, ?, ?, ?)""", (user_id, nickname, 10, 0))
            self.connection.commit()
        except Exception as e:
            return "Ошибка"

    def get_user(self, user_id):
        try:
            return self.cursor.execute("""SELECT * FROM users
                                                WHERE id_user = ?""", (user_id,)).fetchone()

        except Exception as e:
            return "Ошибка"

    def add_voting(self, downvotes_tokens, upvotes_tokens, description):
        try:
            self.cursor.execute("""INSERT INTO votings (upvotes_tokens, upvotes_memb, downvotes_tokens, 
            end_time, description) VALUES (?, ?, ?, ?, ?)""",
                                (upvotes_tokens, 0, downvotes_tokens, get_end_time(self.get_duration()), description))
            self.connection.commit()
        except Exception as e:
            print(e)
            return "Ошибка"

    def get_kvorum(self, downvotes_tokens):
        members = self.cursor.execute("""SELECT tokens_voting FROM users WHERE tokens_voting => ?""", (
            downvotes_tokens,
        )).fetchall()
        kvorum = self.cursor.execute("""SELECT * FROM settings WHERE param = kvorum""").fetchone()
        return (len(members) if kvorum[1] == 'members' else sum(members)) * kvorum[2] / 100

    def get_duration(self):
        return self.cursor.execute("""SELECT * FROM settings WHERE param = 'duration'""").fetchone()[-1]

    def get_type_of_param(self, param):
        return self.cursor.execute("""SELECT * FROM settings WHERE param = ?""", (param, )).fetchone()[1]

    def get_value_of_param(self, param):
        return self.cursor.execute("""SELECT * FROM settings WHERE param = ?""", (param,)).fetchone()[-1]

    def get_params(self):
        return self.cursor.execute("""SELECT param FROM settings""").fetchall()

    def check_admin(self, user_id):
        try:
            result = self.cursor.execute("""SELECT admin FROM users
                                        WHERE id_user = ?""", (user_id,)).fetchone()
            if result is None:
                return "Сперва зарегистрируйтесь в системе"
            return result[0]
        except Exception as e:
            return "Ошибка"

    def create_admin(self, user_id):
        try:
            self.cursor.execute("""UPDATE users SET admin = 1
                                WHERE id_user = ?""", (user_id,))
            self.connection.commit()
        except Exception as e:
            return "Ошибка"

    def close(self):
        self.connection.close()

