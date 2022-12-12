import logging
from random import choice

import redis
import telegram
from dotenv import load_dotenv
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from create_tasks import get_quiz_tasks
from settings import redis_host, redis_password, redis_port, telegram_token

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("quiz_bot")

QUIZ = range(1)

DB = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True,
)


def start(context, update):
    """Send a message when the command /start is issued."""
    custom_keyboard = [["Новый вопрос"], ["Сдаться"], ["Мой счет"]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        "Привет, я бот для викторины!", reply_markup=reply_markup
    )
    return QUIZ


def handle_new_question_request(context, update):
    user_id = update.effective_user.id
    quiz_tasks = get_quiz_tasks()
    question, answer = choice(list(quiz_tasks.items()))
    update.message.reply_text(question)
    DB.set(f"{user_id}_question", question)
    DB.set(f"{user_id}_answer", answer)
    return QUIZ


def handle_solution_attempt(context, update):
    user_answer = update.message.text
    user_id = update.effective_user.id
    answer = DB.get(f"{user_id}_answer")
    if user_answer.lower() in answer.lower():
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        update.message.reply_text(message)
        return QUIZ
    else:
        message = "Неправильно… Попробуешь ещё раз? Для следующего вопроса нажми «Новый вопрос»"
        update.message.reply_text(message)
        return QUIZ


def capitulate(context, update):
    user_id = update.effective_user.id
    answer = DB.get(f"{user_id}_answer")
    update.message.reply_text(answer)
    return QUIZ


def cancel(context, update):
    update.message.reply_text("Goodbye!")


def error(update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    load_dotenv()

    updater = Updater(telegram_token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUIZ: [
                MessageHandler(
                    Filters.regex("Новый вопрос"), handle_new_question_request
                ),
                MessageHandler(Filters.regex("Сдаться"), capitulate),
                MessageHandler(Filters.text, handle_solution_attempt),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
        ],
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
