from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

from tokens import BOT_TOKEN
from handlers import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(Создать заявку)$"), main_menu)
        ],
        states={
            CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_category)
            ],
            ISSUE_TYPE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_issue_type)
            ],
            PROBLEM_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_problem)
            ],
            INSTRUCTIONS_STEP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instructions_response)
            ],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)
            ],
            FULL_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)
            ],
            DEPARTMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_department)
            ],
            CONTACT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)
            ],
            PHOTO: [
                MessageHandler(filters.TEXT | filters.PHOTO, get_photo)
            ],
            INVENTORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_inventory)
            ]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)

    application.add_handler(
        MessageHandler(filters.Regex("^(Мои заявки)$"), main_menu)
    )

    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()