from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import CATEGORIES, ISSUE_TYPES, PROBLEMS


def get_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Создать заявку")],
        [KeyboardButton("Мои заявки")]
    ], resize_keyboard=True)


def get_categories_keyboard():
    categories = list(CATEGORIES.values())
    keyboard = []

    # Разбиваем на строки по 2 кнопки
    for i in range(0, len(categories), 2):
        row = categories[i:i + 2]
        keyboard.append([KeyboardButton(category) for category in row])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_issue_types_keyboard(category: str):
    category_key = [k for k, v in CATEGORIES.items() if v == category][0]
    issue_types = list(ISSUE_TYPES.get(category_key, {}).values())

    keyboard = []
    for issue_type in issue_types:
        keyboard.append([KeyboardButton(issue_type)])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_problems_keyboard(issue_type: str):
    issue_key = None
    for category_issues in ISSUE_TYPES.values():
        for key, value in category_issues.items():
            if value == issue_type:
                issue_key = key
                break
        if issue_key:
            break

    problems = list(PROBLEMS.get(issue_key, {}).values())

    keyboard = []
    for problem in problems:
        keyboard.append([KeyboardButton(problem)])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_instructions_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Проблема решена")],
        [KeyboardButton("Создать заявку")],
    ], resize_keyboard=True)


def get_confirmation_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Да, все работает")],
        [KeyboardButton("Нет, требуется доработка")],
    ], resize_keyboard=True)

def get_skip_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("Пропустить")]], resize_keyboard=True)

def remove_keyboard():
    return ReplyKeyboardRemove()