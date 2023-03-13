import os as _os
import threading as _thread
import time as _time

import dotenv as _env
import schedule as _schedule
import telebot as _tbot

import models as _models

_env.load_dotenv()


API_TOKEN = _os.environ["API_TOKEN"]

bot = _tbot.TeleBot(API_TOKEN)


def _get_user_tasks(chat_id) -> str:
    user = _models.User.get(_models.User.chat_id == chat_id)
    tasks = _models.Todo.select().where(
        _models.Todo.user == user, _models.Todo.is_done == False
    )

    response = []

    if tasks:
        for task in tasks:
            response.append(f"<b>{task.id}. {task.task}</b>\n")
    else:
        response.append("<b>You dont have any tasks</b>")

    return "".join(response)


def _check_tasks():
    for user in _models.User.select():
        tasks = _models.Todo.select().where(
            _models.Todo.user == user, _models.Todo.is_done == False
        )
        if tasks:
            bot.send_message(
                user.chat_id, _get_user_tasks(user.chat_id), parse_mode="HTML"
            )


def _run_scheduler():
    _schedule.every(1).hours.do(_check_tasks)
    while True:
        _schedule.run_pending()
        _time.sleep(1)


@bot.message_handler(commands=["start"])
def start_hadler(message):
    if not _models.User.select().where(
        _models.User.chat_id == message.chat.id
    ):
        _models.User.create(chat_id=message.chat.id)
    bot.send_message(
        message.chat.id, f"Hello, {message.chat.first_name or None}"
    )


@bot.message_handler(commands=["list"])
def get_tasks_list(message):
    bot.send_message(
        message.chat.id, _get_user_tasks(message.chat.id), parse_mode="HTML"
    )


@bot.message_handler(regexp="\d+ done")
def mark_done(message):
    task_id = message.text.split(" ")[0]
    task = _models.Todo.get(_models.Todo.id == task_id)
    task.is_done = True
    task.save()

    bot.send_message(message.chat.id, f"The task is done!")


@bot.message_handler(content_types=["text"])
def create_task_handler(message):
    user = _models.User.get(_models.User.chat_id == message.chat.id)
    _models.Todo.create(
        user=user,
        task=message.text,
    )
    bot.send_message(message.chat.id, "New Task has been created!")


if __name__ == "__main__":
    _thread.Thread(target=_run_scheduler).start()
    bot.infinity_polling()
