import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from aiogram import Router

# Токен бота (замените на ваш)
API_TOKEN = "8321150348:AAHflUwd01X17UMP-xnZRkNmk4NT-JSApl0"
MANAGER_TELEGRAM_ID = 1125654080  # Замените на ID менеджера

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Состояния FSM
class Form(StatesGroup):
    waiting_for_fio = State()
    waiting_for_category = State()
    waiting_for_subcategory = State()
    waiting_for_issue = State()
    waiting_for_checklist = State()
    waiting_for_full_name = State()
    waiting_for_department = State()
    waiting_for_contact = State()
    waiting_for_issue_type = State()
    waiting_for_description = State()
    waiting_for_photo = State()
    waiting_for_inventory = State()

# Кнопка "Отмена"
def cancel_kb():
    kb = [[KeyboardButton(text="❌ Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Главное меню
def main_kb():
    kb = [
        [KeyboardButton(text="Технические проблемы")],
        [KeyboardButton(text="Административные обращения")],
        [KeyboardButton(text="Жалобы и безопасность")],
        [KeyboardButton(text="Коммуникация")],
        [KeyboardButton(text="Экстренный случай")],
        [KeyboardButton(text="Консультации и обучение")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Подкатегории "Технические проблемы"
def tech_subcategories_kb():
    kb = [
        [KeyboardButton(text="Компьютер/Рабочее место")],
        [KeyboardButton(text="Программное обеспечение")],
        [KeyboardButton(text="Сетевые проблемы")],
        [KeyboardButton(text="Оборудование и техника")],
        [KeyboardButton(text="Мобильные устройства")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Проблемы для "Компьютер/Рабочее место"
def computer_issues_kb():
    kb = [
        [KeyboardButton(text="Не включается компьютер")],
        [KeyboardButton(text="Не загружается система")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def software_issues_kb():
    kb = [[KeyboardButton(text="Ошибка при загрузке программы")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def network_issues_kb():
    kb = [[KeyboardButton(text="Нет подключения к интернету")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def hardware_issues_kb():
    kb = [[KeyboardButton(text="Не работает принтер/сканер/клавиатура/мышь")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def mobile_issues_kb():
    kb = [[KeyboardButton(text="Не работает корпоративное приложение")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_fio)
    await message.answer("Привет! Пожалуйста, введите ваше ФИО (только буквы и пробелы):")

# Проверка ФИО
@router.message(Form.waiting_for_fio)
async def process_fio(message: types.Message, state: FSMContext):
    fio = message.text.strip()
    if re.fullmatch(r"[а-яА-ЯёЁ\s]+", fio) and len(fio.split()) >= 2:
        await state.update_data(fio=fio)
        await state.set_state(Form.waiting_for_category)
        await message.answer("Спасибо! Теперь выберите раздел обращения:", reply_markup=main_kb())
    else:
        await message.answer("❌ ФИО должно содержать только буквы и пробелы. Попробуйте снова.")

# Выбор категории
@router.message(Form.waiting_for_category, F.text == "Технические проблемы")
async def process_category_tech(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_subcategory)
    await message.answer("Выберите подраздел:", reply_markup=tech_subcategories_kb())

# Выбор подкатегории
@router.message(Form.waiting_for_subcategory)
async def process_subcategory(message: types.Message, state: FSMContext):
    subcategory = message.text
    if subcategory == "Компьютер/Рабочее место":
        await state.update_data(subcategory=subcategory)
        await state.set_state(Form.waiting_for_issue)
        await message.answer("Выберите проблему:", reply_markup=computer_issues_kb())
    elif subcategory == "Программное обеспечение":
        await state.update_data(subcategory=subcategory)
        await state.set_state(Form.waiting_for_issue)
        await message.answer("Выберите проблему:", reply_markup=software_issues_kb())
    elif subcategory == "Сетевые проблемы":
        await state.update_data(subcategory=subcategory)
        await state.set_state(Form.waiting_for_issue)
        await message.answer("Выберите проблему:", reply_markup=network_issues_kb())
    elif subcategory == "Оборудование и техника":
        await state.update_data(subcategory=subcategory)
        await state.set_state(Form.waiting_for_issue)
        await message.answer("Выберите проблему:", reply_markup=hardware_issues_kb())
    elif subcategory == "Мобильные устройства":
        await state.update_data(subcategory=subcategory)
        await state.set_state(Form.waiting_for_issue)
        await message.answer("Выберите проблему:", reply_markup=mobile_issues_kb())
    else:
        await message.answer("Пока другие разделы не реализованы. Выберите 'Технические проблемы'.")

# Выбор проблемы и вывод чеклиста
@router.message(Form.waiting_for_issue)
async def process_issue(message: types.Message, state: FSMContext):
    issue = message.text
    checklist = {
        "Не включается компьютер": [
            "1. Проверить питание и кабель.",
            "2. Проверить розетку.",
            "3. Попробовать другую розетку.",
            "4. Сделать фото серийного номера.",
            "Если не помогло - оставить заявку."
        ],
        "Не загружается система": [
            "1. Перезагрузить компьютер.",
            "2. Сделать фото экрана ошибки.",
            "Если не помогло - оставить заявку."
        ],
        "Ошибка при загрузке программы": [
            "1. Сделать скриншот ошибки.",
            "2. Проверить обновления.",
            "3. Перезапустить ПК.",
            "4. Проверить интернет.",
            "Если не помогло - оставить заявку."
        ],
        "Нет подключения к интернету": [
            "1. Проверить кабель или Wi-Fi.",
            "2. Перезапустить роутер.",
            "3. Проверить индикаторы сети.",
            "Если не помогло - оставить заявку."
        ],
        "Не работает принтер/сканер/клавиатура/мышь": [
            "1. Проверить питание.",
            "2. Проверить бумагу и картридж / проверить кабель или уровень заряда",
            "Если не помогло - оставить заявку."
        ],
        "Не работает корпоративное приложение": [
            "1. Проверить интернет.",
            "2. Перезапустить приложение.",
            "3. Проверить обновления.",
            "Если не помогло - оставить заявку."
        ]
    }
    if issue in checklist:
        await state.update_data(issue=issue)
        checklist_text = "\n".join(checklist[issue])
        await message.answer(f"Чеклист:\n{checklist_text}")
        await state.set_state(Form.waiting_for_checklist)

# Выбор "оставить заявку"
@router.message(Form.waiting_for_checklist, F.text.contains("оставить заявку"))
async def start_claim(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_full_name)
    await message.answer("Введите ваше ФИО еще раз (для заявки):", reply_markup=cancel_kb())

@router.message(Form.waiting_for_full_name)
async def process_claim_fio(message: types.Message, state: FSMContext):
    fio = message.text.strip()
    if re.fullmatch(r"[а-яА-ЯёЁ\s]+", fio) and len(fio.split()) >= 2:
        await state.update_data(claim_fio=fio)
        await state.set_state(Form.waiting_for_department)
        await message.answer("Введите подразделение:")
    else:
        await message.answer("❌ ФИО некорректно. Попробуйте снова.")

@router.message(Form.waiting_for_department)
async def process_department(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text)
    await state.set_state(Form.waiting_for_contact)
    await message.answer("Введите ваш контакт (телефон +7... или email):")

@router.message(Form.waiting_for_contact)
async def process_contact(message: types.Message, state: FSMContext):
    contact = message.text.strip()
    if re.match(r"^\+7\d{10}$", contact) or re.match(r"[^@]+@[^@]+\.[^@]+", contact):
        await state.update_data(contact=contact)
        data = await state.get_data()
        await state.set_state(Form.waiting_for_issue_type)
        await message.answer(f"Тип неисправности: {data['issue']}.\nВведите подробное описание проблемы:")
    else:
        await message.answer("❌ Некорректный формат контакта. Телефон должен начинаться с +7, email — в формате name@domain.com")

@router.message(Form.waiting_for_issue_type)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Form.waiting_for_photo)
    await message.answer("Пришлите фото/скриншот (или введите 'пропустить'):")

@router.message(Form.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(Form.waiting_for_inventory)
    await message.answer("Введите инвентарный номер техники или рабочее место:")

@router.message(Form.waiting_for_photo)
async def process_no_photo(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    if text == "пропустить":
        await state.update_data(photo=None)
        await state.set_state(Form.waiting_for_inventory)
        await message.answer("Введите инвентарный номер техники или рабочее место:")
    else:
        await message.answer("Пожалуйста, пришлите фото или введите 'пропустить'.")

# Обновлённая функция с отправкой заявки менеджеру
current_ticket_number = 0

@router.message(Form.waiting_for_inventory)
async def process_inventory(message: types.Message, state: FSMContext):
    global current_ticket_number
    current_ticket_number += 1
    ticket_number = f"{current_ticket_number:05d}"

    await state.update_data(inventory=message.text, ticket_number=ticket_number)
    data = await state.get_data()

    # Формируем текст заявки
    response = f"""
✅ Заявка создана!\n
ФИО: {data['claim_fio']}\n
Подразделение: {data['department']}\n
Контакт: {data['contact']}\n
Тип неисправности: {data['issue']}\n
Описание: {data['description']}\n
Инвентарный номер: {data['inventory']}\n
"""
    await message.answer(response)

    # Уведомление пользователю
    await message.answer(f"Ваша заявка №{ticket_number} зарегистрирована. Мы уведомим вас, когда заявка будет выполнена.")

    # Формируем сообщение для менеджера
    manager_msg = f"""
📩 Новая заявка от:
ФИО: {data['claim_fio']}
Подразделение: {data['department']}
Контакт: {data['contact']}
Тип неисправности: {data['issue']}
Описание: {data['description']}
Инвентарный номер: {data['inventory']}
№ заявки: {ticket_number}
"""

    # Отправляем менеджеру
    try:
        await bot.send_message(MANAGER_TELEGRAM_ID, manager_msg)
        if data.get('photo'):
            await bot.send_photo(MANAGER_TELEGRAM_ID, data['photo'], caption="Фото/скриншот от сотрудника")
    except Exception as e:
        print(f"Ошибка при отправке менеджеру: {e}")

    await state.clear()

# Обработчик отмены
@router.message(F.text == "❌ Отмена")
async def cancel_action(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())

# Запуск бота
if __name__ == "__main__":
    dp.include_router(router)
    dp.run_polling(bot)