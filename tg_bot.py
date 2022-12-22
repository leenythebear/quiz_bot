import functools
import logging
import os
from random import choice

import redis
import telegram
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from create_tasks import get_quiz_tasks

logger = logging.getLogger("quiz_bot")


def start(context, update):
    """Send a message when the command /start is issued."""
    custom_keyboard = [["Новый вопрос"], ["Сдаться"], ["Мой счет"]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        "Привет, я бот для викторины!", reply_markup=reply_markup
    )


def handle_new_question_request(context, update, database, quiz_tasks):
    user_id = update.effective_user.id
    question, answer = choice(list(quiz_tasks.items()))
    update.message.reply_text(question)
    database.set(f"{user_id}_question", question)
    database.set(f"{user_id}_answer", answer)


def handle_solution_attempt(context, update, database):
    user_answer = update.message.text
    user_id = update.effective_user.id
    answer = database.get(f"{user_id}_answer")
    if user_answer.lower() in answer.lower():
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        update.message.reply_text(message)
    else:
        message = "Неправильно… Попробуешь ещё раз? Для следующего вопроса нажми «Новый вопрос»"
        update.message.reply_text(message)


def capitulate(context, update, database):
    user_id = update.effective_user.id
    answer = database.get(f"{user_id}_answer")
    update.message.reply_text(answer)


def cancel(context, update):
    update.message.reply_text("Goodbye!")


def get_error(update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    load_dotenv()

    redis_host = os.environ["DB_HOST"]
    redis_port = os.environ["DB_PORT"]
    redis_password = os.environ["DB_PASSWORD"]

    telegram_token = os.environ["TG_TOKEN"]

    questions_path = os.environ["QUESTION_PATH"]

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    updater = Updater(telegram_token)

    dp = updater.dispatcher

    database = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True,
    )
    quiz_tasks = get_quiz_tasks(questions_path)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(
        MessageHandler(
            Filters.regex("Новый вопрос"),
            functools.partial(
                handle_new_question_request,
                database=database,
                quiz_tasks=quiz_tasks,
            ),
        )
    )
    dp.add_handler(
        MessageHandler(
            Filters.regex("Сдаться"),
            functools.partial(capitulate, database=database),
        )
    )
    dp.add_handler(
        MessageHandler(
            Filters.text,
            functools.partial(handle_solution_attempt, database=database),
        )
    )
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_error_handler(get_error)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
