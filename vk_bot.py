import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from create_tasks import get_quiz_tasks
from settings import redis_host, redis_password, redis_port, questions_path, vk_token

DB = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True,
)


def send_question(event, vk_api, database, quiz_tasks):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.SECONDARY)

    user_id = event.user_id

    question, answer = random.choice(list(quiz_tasks.items()))
    database.set(f"{user_id}_question", question)
    database.set(f"{user_id}_answer", answer)
    vk_api.messages.send(
        user_id=user_id, message=question, keyboard=keyboard.get_keyboard(), random_id=random.randint(1, 1000)
    )


def check_answer(event, vk_api, database):
    user_id = event.user_id
    answer = database.get(f"{user_id}_answer")
    user_answer = event.text
    if user_answer.lower() in answer.lower():
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        vk_api.messages.send(
            user_id=user_id, message=message, random_id=random.randint(1, 1000)
        )
    else:
        message = "Неправильно… Попробуешь ещё раз? Для следующего вопроса нажми «Новый вопрос»"
        vk_api.messages.send(
            user_id=user_id, message=message, random_id=random.randint(1, 1000)
        )


def capitulate(event, vk_api, database):
    user_id = event.user_id
    answer = DB.get(f"{user_id}_answer")
    vk_api.messages.send(
        user_id=user_id, message=answer, random_id=random.randint(1, 1000)
    )


if __name__ == "__main__":
    load_dotenv()

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    quiz_tasks = get_quiz_tasks(questions_path)
    database = redis.Redis(host=redis_host, port=redis_port,
                           password=redis_password,
                           decode_responses=True)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Новый вопрос":
                send_question(event, vk_api, database, quiz_tasks)
            elif event.text == "Сдаться":
                capitulate(event, vk_api, database)
            else:
                check_answer(event, vk_api, database)
