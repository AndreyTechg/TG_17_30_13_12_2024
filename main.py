import telebot
from telebot import types
import config
import wikipedia
import re
import random
import sqlite3
from message_handler.linking import ed_message

# создаем бд. Атрибут check_same_thread - позволяет использование
# соединения в разных потоках
conn = sqlite3.connect("users.db", check_same_thread=False)
# объект-курсор для обращение в бд (поиск, добавить, удалить и тд..)
cur = conn.cursor()
# сделали запрос на создание таблицы
cur.execute("CREATE TABLE IF NOT EXISTS users(id INT);")
# сохранялка данных
conn.commit()

bot = telebot.TeleBot(config.token)

game = False
num = False


text = ""
link = ""
admins = [5025000923]
clients = []
statia = ["Москва", "Питер", "Шаурма"]

@bot.message_handler(commands=["random_statia"])
def ran_statia(message):
    choice_statie = random.choice(statia)
    bot.send_message(message.chat.id, get_wiki(choice_statie))


@bot.message_handler(commands=["start"])
def test(message):
    print(message.chat.id)
    if message.chat.id in admins:
        help(message)
    else:
        info = cur.execute("SELECT * FROM users WHERE id=?", (message.chat.id,)).fetchone()
        if not info:
            cur.execute("INSERT INTO users (id) VALUES (?)", (message.chat.id,))
            conn.commit()
            bot.send_message(message.chat.id, "Теперь вы будете получать рассылку!")

    # print(message)
    # markup_inline = types.InlineKeyboardMarkup()
    # btn_y = types.InlineKeyboardButton(text="yes", callback_data="yes")
    # btn_n = types.InlineKeyboardButton(text="no", callback_data="no")
    # markup_inline.add(btn_y, btn_n)
    # bot.send_message(message.chat.id, "Хочешь продолжить?", reply_markup=markup_inline)

def help(message):
    admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # 1- Создать клавиатуру
    admin_markup.add(types.KeyboardButton("Создать текст для рассылки")) # 2 - делаем кнопки для клавиатуры и добавляем в клавиатуру
    admin_markup.add(types.KeyboardButton("Создать ссылку для рассылки")) # 2 - делаем кнопки для клавиатуры и добавляем в клавиатуру
    admin_markup.add(types.KeyboardButton("Показать сообщение для рассылки")) # 2 - делаем кнопки для клавиатуры и добавляем в клавиатуру
    admin_markup.add(types.KeyboardButton("Начать рассылку"))# 2 - делаем кнопки для клавиатуры и добавляем в клавиатуру
    admin_markup.add(types.KeyboardButton("Помощь")) # 2 - делаем кнопки для клавиатуры и добавляем в клавиатуру
    bot.send_message(message.chat.id, "Команды бота: \n"
                                      "/create_text - Создать текст для рассылки. \n"
                                      "/crete_link - Создать ссылку для рассылки. \n"
                                      "/show_message - Показать сообщение для рассылки. \n"
                                      "/start_linking - Начать рассылку. \n"
                                      "/help - Помощь", reply_markup=admin_markup)


@bot.message_handler(commands=["create_text"])
def edit_message(message):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id, "Введи текст для рассылки")
        bot.register_next_step_handler(m, add_text)

def add_text(message):
    global text
    text = message.text
    if text not in ["Скиньтесь админу на покушать"]:
        bot.send_message(message.chat.id, f"Сохраненный текст: {text}")
    else:
        bot.send_message(message.chat.id, "Ошибка")

@bot.message_handler(commands=["crete_link"])
def edit_link(message):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id, "Введи ссылку для рассылки")
        bot.register_next_step_handler(m, add_link)

def add_link(message):
    global link
    regex = re.compile(
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # проверка dot
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # проверка ip 
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if message.text is not None and regex.search(message.text):
        link = message.text
        bot.send_message(message.chat.id, f"Сохранил ссылку: {link}")
    else:
        m = bot.send_message(message.chat.id, "Ссылка некорректная, переделай.")
        bot.register_next_step_handler(m, add_link)


@bot.message_handler(commands=["start_linking"])
def start_linking(message):
    global text, link
    if message.chat.id in admins:
        if text != "":
            if link != "":
                cur.execute("SELECT id FROM users")
                massive = cur.fetchall()
                print(massive)
                for client_id in massive:
                    id = client_id[0]
                    sending(id)
                else:
                    text = ""
                    link = ""
            else:
                bot.send_message(message.chat.id, "Ссылка отсутствует, заполни перед отправкой")
        else:
            bot.send_message(message.chat.id, "Текст отсутствует, заполни перед отправкой")

def sending(id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Ссылка на сайт", url=link))
    bot.send_message(id, text, reply_markup=markup)



@bot.callback_query_handler(func=lambda call:True)
def callback_but(call):
    if call.data == "yes":
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True) # 1- Создать клавиатуру
        btn_id = types.KeyboardButton("id") # 2 - делаем кнопки для клавиатуры
        btn_usr = types.KeyboardButton("usr") # 2 - делаем кнопки для клавиатуры
        markup_reply.add(btn_id, btn_usr) # 3 - добавить в клавиатуру
        bot.send_message(call.message.chat.id, "Что тебе показать?", reply_markup=markup_reply) # 4 - отправка сообщения
        # и прикрепить в качестве сопровождения кнопки


@bot.message_handler(commands=["hello"])
def test(message):
    bot.send_message(message.chat.id, "Отправил сообщение")

@bot.message_handler(commands=["game"])
def game_number(message):
    global game, num
    game = True
    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True) # Создаем реплай клавиатуру
    btn_1 = types.KeyboardButton("1") # создаем кнопку 1
    btn_2 = types.KeyboardButton("2") # создаем кнопку 2
    btn_3 = types.KeyboardButton("3") # создаем кнопку 3
    markup_reply.add(btn_1, btn_2, btn_3) # В клавиатуру вставляем кнопки через метод add (добавить)
    num = random.randint(1, 3) # генерируем рандомное число в диапозоне
    bot.send_message(message.chat.id, "Я загадал число от 1 до 3, угадай!", reply_markup=markup_reply) # бот отправит смс с кнопкой

# content_types - Реагирует на типы сообщений (текст, стикер, смайлики)
@bot.message_handler(content_types=["text"])
def get_text(message):
    if "Привет" == message.text:
        bot.send_message(message.chat.id, "Ты написал привет")
    elif "id" == message.text:
        bot.send_message(message.chat.id, f"Ваш айди: {message.from_user.id}")
    elif "usr" == message.text:
        bot.send_message(message.chat.id, f"Ваш usr: {message.from_user.username}")
    elif str(num) == message.text and message.text in ["1", "2", "3"] and game:
        pass
    elif "Создать текст для рассылки" == message.text:
        edit_message(message)


wikipedia.set_lang("ru")

def get_wiki(word):
    try:
        wiki = wikipedia.page(word)
        wikitext = wiki.content[:1000]
        wiki_result = wikitext.split(".")
        wiki_result = wiki_result[:-1]
        wiki_result_2 = ""
        for i in wiki_result:
            if not ("==" in i):
                wiki_result_2 = wiki_result_2 + i + "."
        wiki_result_2 = re.sub("\([^()]*\)", "", wiki_result_2)
        return wiki_result_2
    except:
        return "Not found page wikipedia"


print(get_wiki("Османская Империя"))

bot.infinity_polling()

