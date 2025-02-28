

def ed_message(message, bot, admins, add_text):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id, "Введи текст для рассылки")
        bot.register_next_step_handler(m, add_text)