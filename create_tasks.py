import argparse


def get_quiz_tasks(path):
    with open(
        path, "r", encoding="KOI8-R"
    ) as questions_file:
        quiz_questions = questions_file.read()
        paragraphs = quiz_questions.split("Вопрос ")[1:]
        questions = []
        answers = []
        for paragraph in paragraphs:
            question = paragraph.split("\n\n")[0].split(":\n")[1]
            answer = paragraph.split("\n\n")[1].split("Ответ:\n")[1]

            questions.append(question)
            answers.append(answer)

        quiz_tasks = dict(zip(questions, answers))
        return quiz_tasks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Quiz-bot для Vk и Telegram")
    parser.add_argument("-p", "--questions_path", help="Указать свой путь к файлу с вопросами", default='quiz-questions/1vs1200.txt')
    args = parser.parse_args()
    get_quiz_tasks(args.questions_path)
