from random import choice

import redis
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    ConversationHandler
import logging
from dotenv import load_dotenv
from main import get_quiz_tasks

from settings import redis_password, redis_port, redis_host, telegram_token

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger('quiz_bot')

QUIZ = range(1)

DB = redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)


def start(context, update):
    """Send a message when the command /start is issued."""
    custom_keyboard = [['Новый вопрос'], ['Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Привет, я бот для викторины!',
                              reply_markup=reply_markup)
    return QUIZ


def handle_new_question_request(context, update, user_data):
    quiz_tasks = get_quiz_tasks()
    question, answer = choice(list(quiz_tasks.items()))
    user_data["question"] = question
    update.message.reply_text(user_data["question"])
    user_data["answer"] = answer
    return QUIZ


def handle_solution_attempt(context, update, user_data):
    user_answer = update.message.text
    answer = user_data["answer"].split(".")
    if user_answer == answer[0]:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        update.message.reply_text(message)
        return QUIZ
    else:
        message = 'Неправильно… Попробуешь ещё раз?'
        update.message.reply_text(message)
        return QUIZ


def capitulate(context, update, user_data):
    answer = user_data["answer"]
    print(answer)
    update.message.reply_text(answer)
    return QUIZ


def cancel(context, update):
    update.message.reply_text("Goodbye!")


# def error(bot, update, error):
#     """Log Errors caused by Updates."""
#     logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    load_dotenv()
    token = os.environ['TG_TOKEN']
    host = os.environ['DB_HOST']
    port = os.environ['DB_PORT']
    password = os.environ['DB_PASSWORD']

    db = redis.Redis(host=host, port=port, password=password, decode_responses=True)

    bot = Bot(token)
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUIZ: [MessageHandler(Filters.regex('Новый вопрос'),
                                  handle_new_question_request, pass_user_data=True),
                   MessageHandler(Filters.regex('Сдаться'), capitulate, pass_user_data=True),
                   MessageHandler(Filters.text,
                                  handle_solution_attempt,
                                  pass_user_data=True),
                   ],
        },
        fallbacks=[CommandHandler("cancel", cancel),
                   ]
    )

    # on noncommand i.e message - echo the message on Telegram

    dp.add_handler(conv_handler)
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
