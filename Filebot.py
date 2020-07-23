from collections import defaultdict
import os
import random
import signal
import pickle
import sys

import telebot

import local_settings

bot = telebot.TeleBot(local_settings.KEY)

if os.path.exists('users.pkl'):
    with open('users.pkl', 'rb') as f:
        users = pickle.load(f)
else:
    users = defaultdict(dict)

print("Users: ", users)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "l come up with a number, you have to guess it! The range is from 1-10.")
    users[message.from_user.username] = [random.randint(1, 10), 3, 10]
    print(users[message.from_user.username])


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message.from_user.username, ": ", message.text)
    chat_id = message.chat.id
    try:
        secret_number = users[message.from_user.username][0]
        attempts = users[message.from_user.username][1]
        level = users[message.from_user.username][2]
    except KeyError:
        bot.send_message(chat_id, "Enter command /start")
        return

    if message.text.isdigit():
        if int(message.text) == secret_number:
            users[message.from_user.username][2] *= 2
            level *= 2
            bot.send_message(chat_id, "BINGO! Next level 1-%s" % level)
            users[message.from_user.username][0] = random.randint(1, level)
            print(users[message.from_user.username])
            return
        elif int(message.text) > level:
            bot.send_message(chat_id,
                             "Very big number.(1-%s)" % level)
            return
        elif int(message.text) < 1:
            bot.send_message(chat_id,
                             "Very small number.(1-%s)" % level)
            return
        elif int(message.text) > int(secret_number):
            users[message.from_user.username][1] -= 1
            attempts -= 1
            bot.send_message(chat_id,
                             "Your number is big. You only have %s attempts left" % attempts)
            return
        elif int(message.text) < int(secret_number):
            users[message.from_user.username][1] -= 1
            attempts -= 1
            bot.send_message(chat_id,
                            "Your number is small. You only have %s attempts left" % attempts)
            return
    else:
        bot.send_message(chat_id, "Send number")


def exit(**args):
    with open('settings.pkl', 'wb') as f:
        pickle.dump(users, f)
    sys.exit(0)


signal.signal(signal.SIGINT, exit)
signal.signal(signal.SIGTERM, exit)

bot.polling()
