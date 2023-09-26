import time

from skpy import SkypeEventLoop, SkypeNewMessageEvent, SkypeCallEvent
import telebot
import os.path
import threading

blocked_chatid = [] # ChatId чатов, по которым не надо присылать уведомления в telegram
silent_notifications_userId = [] #userId пользователей, от которых присылать уведомления без звука в telegram
telegram_chat_id = '' #Ваш chatid в telegram


class MySkypeEventLoop(SkypeEventLoop):
    def onEvent(self, event):
        if isinstance(event, SkypeNewMessageEvent) and event.msg.chatId not in blocked_chatid:

            if event.msg.userId in silent_notifications_userId:
                disable_notification = True
            else:
                disable_notification = False

            print(event.msg)
            print("{}\nНовое сообщение от {}: {}".format(event.msg.chatId, event.msg.user.name, event.msg.content))

            try:
                with open(event.msg.file.name, "wb") as f:
                    f.write(event.msg.fileContent)

                if ".png" in str(event.msg.file.name) or ".jpg" in str(event.msg.file.name):
                    telegram_bot.send_photo(telegram_chat_id, open(event.msg.file.name, "rb"),
                                            caption='<tg-spoiler>' + event.msg.chatId + '</tg-spoiler>' + "\n" + str(
                                                event.msg.user.name), parse_mode="HTML",
                                            disable_notification=disable_notification)
                else:
                    telegram_bot.send_document(telegram_chat_id, open(event.msg.file.name, "rb"),
                                               caption='<tg-spoiler>' + event.msg.chatId + '</tg-spoiler>' + "\n" + str(event.msg.user.name), parse_mode="HTML", disable_notification=disable_notification)


                os.remove(event.msg.file.name)

            except:
                try:
                    telegram_bot.send_message(chat_id=telegram_chat_id,
                                              text="{}\n{}:\n{}".format('<tg-spoiler>' + event.msg.chatId + '</tg-spoiler>', event.msg.user.name,
                                                                        event.msg.content),
                                              parse_mode="HTML",
                                              disable_notification=disable_notification)
                except:
                    telegram_bot.send_message(chat_id=telegram_chat_id,
                                              text="{}\n{}:\n{}".format('<tg-spoiler>' + event.msg.chatId + '</tg-spoiler>', event.msg.user.name,
                                                                        event.msg.content),
                                              disable_notification=disable_notification)
        elif isinstance(event, SkypeCallEvent):
            print(event)
            telegram_bot.send_message(chat_id=telegram_chat_id,
                                      text="Пропущенный звонок")



#УЗ Skype
username = ""
password = ""
skype = MySkypeEventLoop(username, password)

def skype_event_loop():
    skype.loop()

skype_thread = threading.Thread(target=skype_event_loop)
skype_thread.start()


telegram_bot = telebot.TeleBot("") #Bot token

def telegram_thread():
    try:
        @telegram_bot.message_handler(func=lambda message: True)
        def handle_telegram_message(message):
            if message.reply_to_message:
                reply_text = message.reply_to_message.text
                file_caption = message.reply_to_message.caption
                print(reply_text)
                print(file_caption)

                if reply_text is not None:
                    lines = reply_text.splitlines()
                    chat = skype.chats.chat(lines[0])
                    chat.sendMsg(message.text)
                elif file_caption is not None:
                    lines = file_caption.splitlines()
                    chat = skype.chats.chat(lines[0])
                    chat.sendMsg(message.text)
    except Exception as e:
        print(e)
        time.sleep(5)

tel_thread = threading.Thread(target=telegram_thread)
tel_thread.start()


while True:
    try:
        telegram_bot.polling(non_stop=True, interval=0)
    except Exception as e:
        print(e)
        time.sleep(5)
        continue
