import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from create_tasks import get_quiz_tasks
from settings import redis_host, redis_password, redis_port

DB = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True,
)


def start(event, vk_api):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.SECONDARY)
    user_id = event.user_id
    text = "Привет, я бот для викторины!"
    vk_api.messages.send(
        user_id=user_id,
        message=text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000),
    )


def send_question(event, vk_api):
    user_id = event.user_id
    quiz_tasks = get_quiz_tasks()
    question, answer = random.choice(list(quiz_tasks.items()))
    DB.set(f"{user_id}_question", question)
    DB.set(f"{user_id}_answer", answer)
    vk_api.messages.send(
        user_id=user_id, message=question, random_id=random.randint(1, 1000)
    )


def capitulate(event, vk_api):
    user_id = event.user_id
    answer = DB.get(f"{user_id}_answer")
    vk_api.messages.send(
        user_id=user_id, message=answer, random_id=random.randint(1, 1000)
    )


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.environ["VK_TOKEN"]
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Новый вопрос":
                send_question(event, vk_api)
            elif event.text == "Сдаться":
                capitulate(event, vk_api)
            else:
                start(event, vk_api)
