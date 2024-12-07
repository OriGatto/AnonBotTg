from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import uuid

# Замените на ваш токен бота
TOKEN = '7736179898:AAHnN-SS1PH9Jfg-C4tiQq9XoitbjTH--tI'  # Вставьте ваш токен бота здесь

# Словарь для хранения ссылок и соответствующих им пользователей
links = {}

async def start(update: Update, context: CallbackContext) -> None:
    if context.args:
        # Если есть аргументы, значит это ссылка для анонимного вопроса
        link_id = context.args[0]
        if link_id in links:
            await update.message.reply_text('Введите ваше анонимное сообщение:')
            context.user_data['link_id'] = link_id
        else:
            await update.message.reply_text('Неверная ссылка.')
    else:
        # Если нет аргументов, значит это начальное приветствие
        await update.message.reply_text('Привет! Я бот для анонимных вопросов. Нажми /create_link, чтобы создать ссылку для анонимных вопросов.')

async def create_link(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    link_id = str(uuid.uuid4())
    links[link_id] = user_id
    link = f"https://t.me/{context.bot.username}?start={link_id}"
    await update.message.reply_text(f'Ваша ссылка для анонимных вопросов:\n{link}')

async def forward_question(update: Update, context: CallbackContext) -> None:
    if 'link_id' in context.user_data:
        link_id = context.user_data['link_id']
        if link_id in links:
            target_user_id = links[link_id]
            question = update.message.text
            await context.bot.send_message(chat_id=target_user_id, text=f'Анонимный вопрос:\n{question}')
            await update.message.reply_text('Ваш вопрос отправлен.')
            del context.user_data['link_id']
        else:
            await update.message.reply_text('Неверная ссылка.')
    else:
        await update.message.reply_text('Чтобы отправить анонимный вопрос, перейдите по ссылке, которую вам предоставил бот.')

def main() -> None:
    # Создаем объект Application и передаем ему токен бота
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик команды /create_link
    application.add_handler(CommandHandler("create_link", create_link))

    # Регистрируем обработчик для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_question))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()