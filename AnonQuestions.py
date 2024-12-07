from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import uuid

# Замените на ваш токен бота
TOKEN = '7736179898:AAHnN-SS1PH9Jfg-C4tiQq9XoitbjTH--tI'  # Вставьте ваш токен бота здесь

# Словарь для хранения ссылок и соответствующих им пользователей
links = {}

# Словарь для хранения состояния пользователей (отправителей)
user_states = {}

# Список разрешенных получателей, которые могут видеть ссылку на профиль отправителя
# Вставьте сюда юзернеймы разрешенных получателей
allowed_recipients = ['Ori_Gatto', 'radima_02', 'nemustafa', 'mia_tae', 'something_there_7']  # Пример: ['user1', 'user2']

async def start(update: Update, context: CallbackContext) -> None:
    if context.args:
        # Если есть аргументы, значит это ссылка для анонимного вопроса
        link_id = context.args[0]
        if link_id in links:
            await update.message.reply_text('Введите ваше анонимное сообщение:')
            user_states[update.message.from_user.id] = link_id
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
    user_id = update.message.from_user.id
    if user_id in user_states:
        link_id = user_states[user_id]
        if link_id in links:
            target_user_id = links[link_id]
            question = update.message.text
            sender_username = update.message.from_user.username
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Ответить", callback_data=f"reply_{user_id}")]])
            
            # Проверяем, является ли получатель разрешенным
            target_user = await context.bot.get_chat(target_user_id)
            if target_user.username in allowed_recipients:
                message_text = f'Отправитель: @{sender_username}\n\nАнонимное сообщение:\n{question}'
            else:
                message_text = f'Анонимное сообщение:\n{question}'
            
            await context.bot.send_message(chat_id=target_user_id, text=message_text, reply_markup=reply_markup)
            await update.message.reply_text('Ваше сообщение отправлено.')
        else:
            await update.message.reply_text('Неверная ссылка.')
    else:
        await update.message.reply_text('Чтобы отправить анонимное сообщение, перейдите по ссылке, которую вам предоставил бот.')

async def reply_to_anonymous_message(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    sender_id = int(query.data.split('_')[1])
    context.user_data['reply_to_user'] = sender_id
    await query.edit_message_text(text="Введите ваш ответ:")

async def send_reply(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if 'reply_to_user' in context.user_data:
        reply_to_user = context.user_data['reply_to_user']
        reply_message = update.message.text
        await context.bot.send_message(chat_id=reply_to_user, text=f'Ответ на ваше анонимное сообщение:\n{reply_message}')
        await update.message.reply_text('Ваш ответ отправлен.')
        del context.user_data['reply_to_user']
    else:
        await update.message.reply_text('Вы не можете ответить на это сообщение.')

def main() -> None:
    # Создаем объект Application и передаем ему токен бота
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик команды /create_link
    application.add_handler(CommandHandler("create_link", create_link))

    # Регистрируем обработчик для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_question))

    # Регистрируем обработчик для ответов на анонимные сообщения
    application.add_handler(CallbackQueryHandler(reply_to_anonymous_message, pattern='^reply_'))

    # Регистрируем обработчик для отправки ответа
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reply))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()