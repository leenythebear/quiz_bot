import logging
import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from main import get_quiz_tasks

from settings import redis_password, redis_port, redis_host, telegram_token


# from logger import BotLogsHandler

logger = logging.getLogger('quiz-bot')

DB = redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)


def start(event, vk_api):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)
    user_id = event.user_id
    text = 'Привет, я бот для викторины!'
    vk_api.messages.send(user_id=user_id, message=text, keyboard=keyboard.get_keyboard(), random_id=random.randint(1, 1000))


def send_message(event, vk_api, message):
    # quiz_tasks = get_quiz_tasks()
    # question, answer = random.choice(list(quiz_tasks.items()))
    user_id = event.user_id
    quiz_tasks = get_quiz_tasks()
    question, answer = random.choice(list(quiz_tasks.items()))
    DB.set(f'{user_id}_question', question)
    DB.set(f'{user_id}_answer', answer)
    vk_api.messages.send(user_id=user_id, message=question, random_id=random.randint(1, 1000))


def capitulate(event, vk_api):
    user_id = event.user_id
    answer = DB.get(f'{user_id}_answer')
    vk_api.messages.send(user_id=user_id, message=answer, random_id=random.randint(1, 1000))


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.environ['VK_TOKEN']
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            quiz_tasks = get_quiz_tasks()
            question, answer = random.choice(list(quiz_tasks.items()))

            if event.text == 'Новый вопрос':
                send_message(event, vk_api, question)
            elif event.text == 'Сдаться':
                send_message(event, vk_api, answer)
            else:
                start(event, vk_api)
