import sqlite3

class BotDb:
    def __init__(self, file) -> None:
        self.conn = sqlite3.connect(file)
        self.cursor = self.conn.cursor()
    
    def get_user(self, id):
        """Достаем юзерa"""
        result = self.cursor.execute("SELECT user_id FROM users WHERE user_id=(?)", (id, ))
        return result.fetchall()
    
    def get_users(self):
        """Достаем юзеров из базы"""
        result = self.cursor.execute("SELECT user_id FROM users")
        return result.fetchall()

    def add_user(self, id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (id, ))
        return self.conn.commit()

