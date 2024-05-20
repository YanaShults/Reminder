import sqlite3

import data_with_freq


class ReminderDatabase:
    def __init__(self, db_name="reminders.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    # создание таблицы с частотой упоминаний и с данными пользователей
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminder_frequency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                frequency TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                telegram_id INTEGER UNIQUE
            )
        ''')
        self.conn.commit()

    # создание таблицы для напоминаний пользователей (для каждого пользователя своя таблица)
    def create_user_table(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_{} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                datetime DATETIME NOT NULL,
                frequency_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (frequency_id) REFERENCES reminder_frequency(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        '''.format(user_id))
        self.conn.commit()

    # добавление частоты
    def add_reminder_frequency(self, frequencies):
        for frequency in frequencies:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO reminder_frequency (frequency)
                VALUES (?)
            ''', (frequency,))
        self.conn.commit()

    # посмотреть все частоты
    def get_reminder_frequency(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT frequency, id
            FROM reminder_frequency''')
        return cursor.fetchall()

    # добавления пользователя в таблицу с пользователями
    def add_user(self, username, telegram_id=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, telegram_id)
            VALUES (?, ?)
        ''', (username, telegram_id))
        user_id = cursor.lastrowid
        self.create_user_table(user_id)  # Создаем отдельную таблицу напоминаний для нового пользователя
        self.conn.commit()
        return user_id

    # добавить упоминание
    def add_reminder(self, user_id, title, description, datetime_obj, frequency):
        self.add_reminder_frequency(frequency)  # Добавляем вариант частоты, если его еще нет
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO user_{} (title, description, datetime, frequency_id, user_id)
            SELECT ?, ?, ?, id, ? 
            FROM reminder_frequency 
            WHERE frequency = ?
        '''.format(user_id), (title, description, datetime_obj, user_id, frequency))
        self.conn.commit()

    # получить все упоминания
    def get_reminders(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT title, description, datetime, reminder_frequency.frequency 
            FROM user_{}
            JOIN reminder_frequency ON user_{}.frequency_id = reminder_frequency.id
            WHERE user_{}.frequency_id = reminder_frequency.id
        '''.format(user_id, user_id, user_id))
        return cursor.fetchall()

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = ReminderDatabase()

    # Пример добавления пользователя
    # username = "user1"
    # telegram_id = 123456789
    ## user_id = db.add_user(username, telegram_id)

    # Пример добавления напоминания для пользователя
    # title = "Посадить цветы"
    # description = "Купить горшки и семена для цветов"
    # datetime_obj = datetime(2024, 5, 15, 10, 0, 0)
    # frequency = "каждый месяц"
    # db.add_reminder(user_id, title, description, datetime_obj, frequency)

    # Получение всех напоминаний для определенного пользователя
    # reminders = db.get_reminders(user_id)
    # for reminder in reminders:
    #     print(reminder)
    # print(reminders)

    # проверка добавления частоты и вывода данных из таблицы с частотами
    db.add_reminder_frequency(data_with_freq.frequencies)
    a = db.get_reminder_frequency()
    print(a)

    db.close()
