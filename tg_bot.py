import os
from random import choice

import redis
import telegram
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from dotenv import load_dotenv
from main import get_quiz_tasks

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger('quiz_bot')


def start(bot, update):
    """Send a message when the command /start is issued."""
    custom_keyboard = [['Новый вопрос'], ['Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Привет, я бот для викторины!', reply_markup=reply_markup)


def help(context, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def start_game(context, update):
    """Echo the user message."""
    if update.message.text == 'Новый вопрос':
        update.message.reply_text('Играем!')
    if update.message.text == 'Сдаться':
        update.message.reply_text('Очень жаль, приходи играть еще!')
    if update.message.text == 'Мой счет':
        update.message.reply_text('Твой счет:...')


def get_new_question(context, update):
    user_id = update.message.from_user.id
    quiz_tasks = get_quiz_tasks()
    question = choice(list(quiz_tasks.keys()))
    update.message.reply_text(question)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


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
    dp.add_handler(CommandHandler("start", start_game))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.regex('Новый вопрос'), get_new_question))

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
