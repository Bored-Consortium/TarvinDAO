import sqlite3
from get_time import get_end_time


class SqliteConnection:
    def __init__(self):
        self.connection = sqlite3.connect('data/information.db')
        self.cursor = self.connection.cursor()

    def stupid_errors(function):
        def wrapper(*args):
            try:
                return function(*args)
            except Exception as e:
                return "Ошибка"

        return wrapper

    @stupid_errors
    def add_user(self, user_id, nickname, ton):
        self.cursor.execute("""INSERT INTO users (id_user, username, ton) 
                                VALUES (?, ?, ?)""", (user_id, nickname, ton))
        self.connection.commit()

    @stupid_errors
    def check_user(self, user_id):
        result = self.cursor.execute("""SELECT id_user FROM users
                                                    WHERE id_user = ?""", (user_id,)).fetchone()
        return bool(result)

    @stupid_errors
    def get_user(self, user_id):
        return self.cursor.execute("""SELECT * FROM users
                                            WHERE id_user = ?""", (user_id,)).fetchone()

    @stupid_errors
    def get_users_id(self):
        return self.cursor.execute("""SELECT id_user FROM users""").fetchall()

    @stupid_errors
    def add_voting(self, bottom_threshold, upside_threshold, description):
        self.cursor.execute("""INSERT INTO votings (upside_threshold, bottom_threshold, 
        end_time, description) VALUES (?, ?, ?, ?)""",
                            (upside_threshold, bottom_threshold, get_end_time(1), description))
        self.connection.commit()

    @stupid_errors
    def get_last_id_voting_from_description(self, description):
        result = self.cursor.execute("""SELECT id_voting FROM votings 
                                            WHERE description = ?""", (description,)).fetchall()
        return max(list(map(lambda x: x[0], result)))

    @stupid_errors
    def get_current_voting_description(self):
        return self.cursor.execute("""SELECT description FROM votings""").fetchall()

    @stupid_errors
    def get_vote(self, user_id, voting_id):
        return self.cursor.execute("""SELECT * FROM votes
                                    WHERE id_user = ? AND id_voting = ?""", (user_id, voting_id)).fetchone()

    @stupid_errors
    def check_admin(self, user_id):
        result = self.cursor.execute("""SELECT admin FROM users
                                    WHERE id_user = ?""", (user_id,)).fetchone()
        if result is None:
            return "Сперва зарегистрируйтесь в системе"
        return result[0]

    @stupid_errors
    def create_admin(self, user_id):
        self.cursor.execute("""UPDATE users SET admin = 1
                            WHERE id_user = ?""", (user_id,))
        self.connection.commit()

    @stupid_errors
    def create_message_vote(self, message_id, voting_id, user_id):
        self.cursor.execute("""INSERT INTO message_votes (id_message, id_voting, id_user) 
                                    VALUES (?, ?, ?)""", (message_id, voting_id, user_id))
        self.connection.commit()

    @stupid_errors
    def get_message_vote(self, message_id):
        return self.cursor.execute("""SELECT * FROM message_votes 
                                            WHERE id_message = ?""", (message_id,)).fetchone()

    @stupid_errors
    def add_vote(self, user_id, voting_id, tokens, vote):
        self.cursor.execute("""INSERT INTO votes (id_user, id_voting, tokens, vote)
                            VALUES (?, ?, ?, ?)""", (user_id, voting_id, tokens, vote))
        self.cursor.execute("""UPDATE votings 
                            SET upvotes_tokens = upvotes_tokens + ?, 
                                                upvotes_memb = upvotes_memb + 1, 
                                                downvotes_tokens = downvotes_tokens + ?
                            WHERE id_voting = ?""", (tokens * vote, tokens * (1 - vote), voting_id))
        self.connection.commit()

    @stupid_errors
    def get_all_votings(self):
        return self.cursor.execute("""SELECT * FROM votings""").fetchall()

    def get_voting(self, voting_id):
        return self.cursor.execute("""SELECT * FROM votings 
                                        WHERE id_voting = ?""", (voting_id,)).fetchone()

    def change_balance(self, user_id, balance):
        self.cursor.execute("""UPDATE users SET tokens_voting = ? 
                                WHERE id_user = ?""", (balance, user_id))
        self.connection.commit()

    def close(self):
        self.connection.close()
