from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update
import json
import datetime
import os
from dotenv import load_dotenv

#import requests
#import aiohttp

load_dotenv()  # Загружает переменные из файла .env
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

DB_FILE_PATH = r"C:\Users\My Comp\Desktop\TelegramBot\birthday_bot\db3.json"

#access_key = '-5u05_aIm2BiO1s-IQ5OMD0PIi3iiuqk14hY1aJ_2kI'

# Варианты языков
LANGUAGES = {
    'en': {
        'greeting': 
"Hello! Use the following commands:\n"
"/add - to add a record\n"
"/list - to view all records\n"
"/delete - to delete a record by name\n"
"/deleteall - to delete all records\n"
"/birthday - to see who has a birthday today\n"
"/notify - for birthday reminders (once a day)\n"
"/stop_notify - for stop birthday reminders\n",

        'language_prompt': 'Please choose your language / Пожалуйста, выберите язык:',
        'language_change': 'Language changed to English.',
        'add_prompt_name': 'Enter name:',
        'add_prompt_date': 'Enter date (DD.MM):',
        'list_empty': 'The list is empty.',
        'record_saved': 'Data saved.',
        'delete_prompt': 'Enter name to delete:',
        'deleted': "All records with name {name} have been deleted.",
        'confirm_delete_all': 'Are you sure you want to delete all? Type "yes" to confirm.',
        'all_deleted': 'All records have been deleted.',
        'birthday_today': "Today is the birthday of: ",
        'no_birthdays': 'No birthdays today.',
        'unknown_command': 'Unknown command. Use /help for assistance.',
        'reminder_stopped': 'Reminders stopped.',
        'task_not_found': 'Task not found.',
        'task_found': 'Task already stopped.',
        
    },
    'ru': {
        'greeting': 
    "Привет! Используйте:\n"
    "/add - для добавления записи\n"
    "/list - для просмотра всех записей\n"
    "/delete - для удаления одной записи по имени\n"
    "/deleteall - для удаления всех записей\n"
    "/birthday - для вывода списка тех, у кого сегодня др\n"
    "/notify - для напоминаний о днях рождения (раз в день)\n"
    "/stop_notify - для остановки напоминаний\n",
    
        'language_prompt': 'Пожалуйста, выберите язык / Please choose your language:',
        'language_change': 'Язык изменен на Русский.',
        'add_prompt_name': 'Введите имя:',
        'add_prompt_date': 'Введите дату (ДД.ММ):',
        'list_empty': 'Список пуст.',
        'record_saved': 'Данные сохранены.',
        'delete_prompt': 'Введите имя для удаления:',
        'deleted': "Все записи с именем {name} были удалены.",
        'confirm_delete_all': 'Вы действительно хотите удалить все? Введите "да" для подтверждения.',
        'all_deleted': 'Все записи были удалены.',
        'birthday_today': "Сегодня день рождения у: ",
        'no_birthdays': 'Сегодня нет дней рождения.',
        'unknown_command': 'Неизвестная команда. Используйте /help для помощи.',
        'reminder_stopped': 'Напоминания остановлены.',
        'task_not_found': 'Задача не найдена.',
        'task_found': 'Задача уже остановлена.',
    }
}

ASK_NAME, ASK_DATE = range(2)
DELETE_NAME = 1
ANSWER = 1

# Стартовое сообщение с запросом языка
async def start(update, context):
    await update.message.reply_text("Please select language: type 'en' for English, 'ru' for Russian.")
    # Отправляем уведомление владельцу
    owner_id = 1457103158  # вставьте сюда свой ID
    user_id = update.message.from_user.id  # вставьте сюда свой ID
    user_name = update.message.from_user.full_name
    if user_id != owner_id:
        await context.bot.send_message(
            chat_id=owner_id,
            text=f"Пользователь {user_name} ({user_id}) начал работу с ботом."
        )

def get_text(update, context, key):
    lang = context.user_data.get('lang', 'en')
    return LANGUAGES[lang][key]

# Команда для смены языка
async def change_language(update, context):
    await update.message.reply_text(get_text(update, context, 'language_prompt'))  

# Обработка выбора языка
async def set_language(update, context):
    text = update.message.text
    if text == 'en':
        context.user_data['lang'] = 'en'
        await update.message.reply_text(get_text(update, context, 'language_change'))
    elif text == 'ru':
        context.user_data['lang'] = 'ru'
        await update.message.reply_text(get_text(update, context, 'language_change'))
    else:
        # Если выбор не распознан, по умолчанию
        context.user_data['lang'] = 'en'
        await update.message.reply_text(get_text(update, context, 'language_change'))

    await update.message.reply_text(get_text(update, context, 'greeting'))

# Открываем и загружаем JSON файл по указанному пути
def load_data():
    with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
          
# Начинаем добавление /add
async def add(update, context):
    await update.message.reply_text(get_text(update, context, 'add_prompt_name'))
    return ASK_NAME

async def save_name(update, context):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(get_text(update, context, 'add_prompt_date'))
    return ASK_DATE

async def save_date(update, context):
    context.user_data['date'] = update.message.text
    # сохраняем данные в файл
    data = load_data()
    data.append({'name': context.user_data['name'], 'date': context.user_data['date']})
    with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    await update.message.reply_text(get_text(update, context, 'record_saved'))
    return ConversationHandler.END   
    
# Функция, которая сработает на команду /list 
async def list(update, context):
    data = load_data()
    if not data:  # проверка, что список пустой или None
        await update.message.reply_text(get_text(update, context, 'list_empty'))
        return 
    reply = "\n".join([f"{item['name']} - {item['date']}" for item in data])
    await update.message.reply_text(reply)
    
# Функция, которая сработает на команду /delete 
async def delete(update, context):
    await update.message.reply_text(get_text(update, context, 'delete_prompt'))
    return DELETE_NAME

async def delete_name(update, context):
    name = update.message.text
    data = load_data()
    new_data = [item for item in data if item['name'] != name]
    save_data(new_data)
    await update.message.reply_text(get_text(update, context, 'deleted').format(name=name))
    return ConversationHandler.END

# Функция, которая сработает на команду /deleteall 
async def deleteall(update, context):
    await update.message.reply_text(get_text(update, context, 'confirm_delete_all'))
    return ANSWER

async def delete_all(update, context):
    save_data([])
    await update.message.reply_text(get_text(update, context,'all_deleted'))
    return ConversationHandler.END

# Функция для вывода имен, у которых день рождения сегодня
async def birthday(update, context):
    print("Вызов send_birthday")
    data = load_data()
    today = datetime.date.today()
    today_str = today.strftime("%d.%m")
    birthdays_today = [item['name'] for item in data if item['date'] == today_str]
    if birthdays_today:
        reply = get_text(update, context, 'birthday_today')  + " , ".join(birthdays_today)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
 
async def send_birthday(context):
    print("Вызов send_birthday")
    job_data = context.job.data
    chat_id = job_data['chat_id']
    lang = job_data['lang']
    messages = LANGUAGES[lang]
    data = load_data()
    today = datetime.date.today()
    today_str = today.strftime("%d.%m")
    birthdays_today = [item['name'] for item in data if item['date'] == today_str]
    if birthdays_today:
        reply = messages['birthday_today'] + ", ".join(birthdays_today)
        await context.bot.send_message(chat_id=chat_id, text=reply)

# Функция напоминаний о днях рождения
async def notify(update, context):
    chat_id = update.message.chat_id
    lang = context.user_data.get('lang', 'en')
    #запуск повторяющейся задачи
    job = context.job_queue.run_repeating(
        send_birthday, 
        interval=10,
        first=1,
        data={'chat_id':chat_id, 'lang': lang}
        )     
    context.user_data['notify_job'] = job

async def stop_notify(update, context):
    job = context.user_data.get('notify_job')
    if job:
        if job in context.job_queue.jobs():
            job.schedule_removal()
            await update.message.reply_text(get_text(update, context, 'reminder_stopped'))
        else:
            await update.message.reply_text(get_text(update, context, 'task_found'))
        # Удаляем из user_data
        del context.user_data['notify_job']
    else:
        await update.message.reply_text(get_text(update, context, 'task_not_found'))
                
def main():
    # Создаём приложение и передаём токен
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)],
            ASK_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_date)],
        },
        fallbacks=[])
    delete_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', delete)],
        states={
            DELETE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_name)],
        },
        fallbacks=[]
    )
    
    deleteall_handler = ConversationHandler(
        entry_points=[CommandHandler('deleteall', deleteall)],
        states={
            ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_all)],
        },
        fallbacks=[]
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('list', list))
    app.add_handler(delete_handler)
    app.add_handler(CommandHandler('birthday', birthday))
    app.add_handler(deleteall_handler)
    app.add_handler(CommandHandler('notify', notify))
    #app.add_handler(CommandHandler('mem', mem))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_language))
    app.add_handler(CommandHandler('stop_notify', stop_notify))
    
    print("Бот запущен! Нажми Ctrl+C, чтобы остановить.")

    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
    
   