import asyncio
# aiosqlite для работы с асинхронными запросами к базе данных
import aiosqlite
from datetime import datetime, timedelta
from pytz import timezone


class CheckTime:
    def __init__(self, db_name="reminders.db"):
        self.db_name = db_name
        self.timezone = timezone("Europe/Moscow")  # Ваш часовой пояс
        self.loop = asyncio.get_event_loop()

    async def send_reminder(self, user_id, message):
        # Ваш код отправки сообщения пользователю user_id с текстом message
        # print(f"Sending reminder to user {user_id}: {message}")
        return True

    async def check_reminders(self):
        async with aiosqlite.connect(self.db_name) as db:
            while True:
                current_time = datetime.now(self.timezone)
                async with db.execute('''
                    SELECT r.id, r.user_id, r.title, r.description, r.datetime, f.frequency
                    FROM reminders r
                    INNER JOIN reminder_frequency f ON r.frequency_id = f.id
                ''') as cursor:
                    reminders = await cursor.fetchall()

                    for reminder in reminders:
                        reminder_id, user_id, title, description, reminder_time, frequency = reminder
                        # Проверяем, наступило ли время отправки напоминания
                        if current_time >= reminder_time:
                            # Отправляем напоминание
                            message = f"{title}: {description}"
                            await self.send_reminder(user_id, message)

                            # Если частота "разово", удаляем напоминание из базы данных
                            if frequency == "разово":
                                await db.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
                            # Если частота не "разово", обновляем время напоминания в соответствии с частотой
                            else:
                                if frequency == "каждый день":
                                    new_time = reminder_time + timedelta(days=1)
                                elif frequency == "каждую неделю":
                                    new_time = reminder_time + timedelta(weeks=1)
                                elif frequency == "каждый месяц":
                                    new_time = reminder_time + timedelta(days=30)  # Приблизительно каждый месяц
                                elif frequency == "каждый год":
                                    new_time = reminder_time + timedelta(days=365)  # Приблизительно каждый год

                                await db.execute('UPDATE reminders SET datetime = ? WHERE id = ?',
                                                 (new_time, reminder_id))

                            await db.commit()

                # Ждем 1 минуту перед следующей проверкой
                await asyncio.sleep(60)

    def run(self):
        self.loop.create_task(self.check_reminders())
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()


if __name__ == "__main__":
    bot = CheckTime()
    bot.run()
