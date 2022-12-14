# Бот для проведения викторин в Telegram и VK

## Как установить

1. Скачайте код
2. Для работы скрипта нужен Python версии не ниже 3.7
3. Установите зависимости, указанные в файле ``requirements.txt`` командой:

   ```pip install -r requirements.txt```
5. Создайте бота для работы в Telegram и получите его токен
6. Создайте  группу для работы в VK и получите токен группы
7. Создайте базу данных в [Redis](https://redis.com/)
8. Создайте в корне проекта файл ``.env`` и укажите в нем все вышеуказанные данные, по образцу:

```
TG_TOKEN=токен, полученный в п.5
VK_TOKEN=токен, полученный в п.6
DB_HOST=хост базы данных из п. 7 
DB_PORT=порт базы данных из п. 7 
DB_PASSWORD=пароль к базу данных из п. 7 
QUESTION_PATH=путь к файлу с вопросами для викторины
```

## Как запустить
- Telegram-бот запускается командой:

```python3 tg_bot.py```

- Vk-бот запускается командой:

```python3 vk_bot.py```

## Результат работы

Результатом выполнения скриптов будет сообщение с вопросом и возможность указать свой ответ или сдаться.


Попробовать ботов в действии можно по следующим ссылкам:

[Telegram-бот](https://t.me/Leeny_the_bear_bot)

[Vk-бот](https://vk.com/im?sel=-215364307)

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).

## Автор проекта

Елена Иванова [Leeny_the_bear](https://github.com/leenythebear)

