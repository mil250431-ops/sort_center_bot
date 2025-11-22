from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import logging
import re

from config import INSTRUCTIONS
from tokens import ADMIN_CHAT_ID
from database import TicketDatabase
from keyboards import *

(CATEGORY, ISSUE_TYPE, PROBLEM_SELECTION, INSTRUCTIONS_STEP,
 DESCRIPTION, FULL_NAME, DEPARTMENT, CONTACT, PHOTO, INVENTORY) = range(10)

db = TicketDatabase()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

current_ticket_number = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = f"""
Добро пожаловать!

Я - бот сервисного центра. Я помогу вам:
- Создать заявку на техническую поддержку
- Отслеживать статус ваших заявок
- Получить помощь по различным вопросам

Выберите действие:
    """

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu()
    )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Создать заявку":
        await update.message.reply_text(
            "Выберите категорию обращения:",
            reply_markup=get_categories_keyboard()
        )
        return CATEGORY

    elif text == "Мои заявки":
        user_tickets = db.get_user_tickets(update.message.from_user.id)

        if not user_tickets:
            await update.message.reply_text(
                "У вас пока нет созданных заявок.",
                reply_markup=get_main_menu()
            )
            return ConversationHandler.END

        tickets_text = "Ваши заявки:\n\n"
        for ticket in user_tickets[:10]:  # Последние 10 заявок
            tickets_text += f"Заявка #{ticket['id']}\n"
            tickets_text += f"{ticket['problem']}\n"
            tickets_text += f"{ticket['created_at']}\n"
            tickets_text += f"Статус: {ticket['status']}\n\n"

        await update.message.reply_text(
            tickets_text,
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text

    if category not in CATEGORIES.values():
        await update.message.reply_text(
            "Пожалуйста, выберите категорию из предложенных:",
            reply_markup=get_categories_keyboard()
        )
        return CATEGORY

    context.user_data['category'] = category

    await update.message.reply_text(
        f"Выберите тип обращения для категории '{category}':",
        reply_markup=get_issue_types_keyboard(category)
    )

    return ISSUE_TYPE


async def select_issue_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    issue_type = update.message.text

    valid_issue_types = []
    for category_issues in ISSUE_TYPES.values():
        valid_issue_types.extend(category_issues.values())

    if issue_type not in valid_issue_types:
        await update.message.reply_text(
            "Пожалуйста, выберите тип обращения из предложенных:",
            reply_markup=get_issue_types_keyboard(context.user_data['category'])
        )
        return ISSUE_TYPE

    context.user_data['issue_type'] = issue_type

    await update.message.reply_text(
        f"Выберите конкретную проблему:",
        reply_markup=get_problems_keyboard(issue_type)
    )

    return PROBLEM_SELECTION


async def select_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    problem = update.message.text

    valid_problems = []
    for problem_dict in PROBLEMS.values():
        valid_problems.extend(problem_dict.values())

    if problem not in valid_problems:
        await update.message.reply_text(
            "Пожалуйста, выберите проблему из предложенных:",
            reply_markup=get_problems_keyboard(context.user_data['issue_type'])
        )
        return PROBLEM_SELECTION

    context.user_data['problem'] = problem

    problem_key = None
    for key, problems_dict in PROBLEMS.items():
        for p_key, p_value in problems_dict.items():
            if p_value == problem:
                problem_key = p_key
                break
        if problem_key:
            break

    instruction = INSTRUCTIONS.get(problem_key, """
К сожалению, для данной проблемы нет автоматических инструкций.
Пожалуйста, создайте заявку для получения помощи от специалиста.
    """)

    await update.message.reply_text(
        instruction,
        reply_markup=get_instructions_keyboard(),
        parse_mode='Markdown'
    )

    return INSTRUCTIONS_STEP


async def handle_instructions_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text

    if response == "Проблема решена":
        await update.message.reply_text(
            "Рады, что смогли помочь!",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END

    elif response == "Создать заявку":
        await update.message.reply_text(
            "Опишите проблему более подробно:\n\n"
            "• Что именно произошло?\n"
            "• Когда проблема возникла?\n"
            "• Какие действия уже предприняты?",
            reply_markup=remove_keyboard()
        )
        return DESCRIPTION

    else:
        await update.message.reply_text(
            "Пожалуйста, выберите один из вариантов:",
            reply_markup=get_instructions_keyboard()
        )
        return INSTRUCTIONS_STEP


async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    context.user_data['description'] = description

    await update.message.reply_text(
        "Введите ваше ФИО (только буквы и пробелы):"
    )
    return FULL_NAME


async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text.strip()

    if not re.fullmatch(r"[а-яА-ЯёЁ\s]+", full_name) or len(full_name.split()) < 2:
        await update.message.reply_text(
            "❌ ФИО должно содержать только буквы и пробелы (минимум 2 слова). Попробуйте снова:"
        )
        return FULL_NAME

    context.user_data['full_name'] = full_name

    await update.message.reply_text("Введите ваше подразделение/отдел:")
    return DEPARTMENT


async def get_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    department = update.message.text
    context.user_data['department'] = department

    await update.message.reply_text(
        "Введите ваш контакт (телефон в формате +7XXXXXXXXXX, 8XXXXXXXXXX или email):"
    )
    return CONTACT


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.text.strip()

    if not (re.match(r"^\+7\d{10}$", contact) or
            re.match(r"^8\d{10}$", contact) or
            re.match(r"[^@]+@[^@]+\.[^@]+", contact)):
        await update.message.reply_text(
            "❌ Некорректный формат контакта.\n"
            "Телефон должен быть в формате: +7XXXXXXXXXX или 8XXXXXXXXXX\n"
            "Email должен быть в формате: name@domain.com\n"
            "Попробуйте снова:"
        )
        return CONTACT

    context.user_data['contact'] = contact

    await update.message.reply_text(
        "Пришлите фото проблемы:",
        reply_markup=get_skip_keyboard()
    )
    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        context.user_data['photo'] = photo
        await update.message.reply_text(
            "Фото принято!",
            reply_markup=remove_keyboard()
        )
    elif update.message.text and update.message.text.strip() == "Пропустить":
        context.user_data['photo'] = None
        await update.message.reply_text(
            "Хорошо, продолжаем без фото.",
            reply_markup=remove_keyboard()
        )
    else:
        await update.message.reply_text(
            "Пожалуйста, пришлите фото или нажмите 'Пропустить':",
            reply_markup=get_skip_keyboard()
        )
        return PHOTO

    await update.message.reply_text("Введите инвентарный номер техники или рабочее место:")
    return INVENTORY


async def get_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inventory_number = update.message.text
    context.user_data['inventory_number'] = inventory_number

    user = update.message.from_user

    ticket_id = db.create_ticket(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=context.user_data['full_name'],
        department=context.user_data['department'],
        contact=context.user_data['contact'],
        photo=context.user_data.get('photo'),
        inventory_number=inventory_number,
        category=context.user_data['category'],
        issue_type=context.user_data['issue_type'],
        problem=context.user_data['problem'],
        description=context.user_data['description']
    )

    user_response = f"""
Заявка #{ticket_id} создана!

ФИО: {context.user_data['full_name']}
Подразделение: {context.user_data['department']}
Контакт: {context.user_data['contact']}
Категория: {context.user_data['category']}
Тип обращения: {context.user_data['issue_type']}
Проблема: {context.user_data['problem']}
Описание: {context.user_data['description']}
Инвентарный номер: {inventory_number}
"""

    await update.message.reply_text(
        user_response,
        reply_markup=get_main_menu()
    )

    # Уведомление администратора
    if ADMIN_CHAT_ID:
        try:
            admin_message = f"""
Новая заявка #{ticket_id}

ФИО: {context.user_data['full_name']}
Подразделение: {context.user_data['department']}
Контакт: {context.user_data['contact']}
Категория: {context.user_data['category']}
Тип обращения: {context.user_data['issue_type']}
Проблема: {context.user_data['problem']}
Описание: {context.user_data['description']}
Инвентарный номер: {inventory_number}
Создана: {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""

            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_message
            )

            if context.user_data.get('photo'):
                await context.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=context.user_data['photo'],
                    caption=f"Фото к заявке #{ticket_id}"
                )

        except Exception as e:
            logger.error(f"Не удалось уведомить администратора: {e}")

    context.user_data.clear()
    return ConversationHandler.END