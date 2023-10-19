import sqlite3
from get_time import get_end_time


class SqliteConnection:
    def __init__(self):
        self.connection = sqlite3.connect('data/information.db')
        self.cursor = self.connection.cursor()

    def add_user(self, user_id, nickname, ton):
        try:
            self.cursor.execute("""INSERT INTO users (id_user, username, ton) 
                                    VALUES (?, ?, ?)""", (user_id, nickname, ton))
            self.connection.commit()
        except Exception as e:
            return "Ошибка"

    def check_user(self, user_id):
        result = self.cursor.execute("""SELECT id_user FROM users
                                                    WHERE id_user = ?""", (user_id,)).fetchone()
        return bool(result)

    def get_user(self, user_id):
        try:
            return self.cursor.execute("""SELECT * FROM users
                                                WHERE id_user = ?""", (user_id,)).fetchone()

        except Exception as e:
            return "Ошибка"

    def add_voting(self, bottom_threshold, upside_threshold, description):
        try:
            self.cursor.execute("""INSERT INTO votings (upside_threshold, bottom_threshold, 
            end_time, description) VALUES (?, ?, ?, ?)""",
                                (upside_threshold, bottom_threshold, get_end_time(self.get_duration()), description))
            self.connection.commit()
        except Exception as e:
            print(e)
            return "Ошибка"

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

