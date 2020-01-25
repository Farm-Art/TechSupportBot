import os
from sys import executable
from time import sleep

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from config import TOKEN
from convo import *


def setup_proxy_and_start(token, proxy=True):
    address = "orbtl.s5.opennetwork.cc"
    port = 999
    username = "529949097"
    password = "Yf3QaTKO"
    try:
        updater = Updater(
            token,
            request_kwargs={
                'proxy_url': f'socks5://{address}:{port}/',
                'urllib3_proxy_kwargs': {
                    'username': username,
                    'password': password}} if proxy else None,
            use_context=True)
        print('Proxy - OK!')
        main(updater)
    except RuntimeError:
        sleep(1)
        print('PySocks не установлен!')
        os.system(f'{executable} -m pip install pysocks --user')


def main(updater):
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', IdleController(0).start)],
        states={
            IdleController.IDLE: [MessageHandler(Filters.all, IdleController(0))],
            IdleController.REGISTER: [MessageHandler(Filters.text, RegisterSurname())],
            IdleController.QUEUE: [MessageHandler(Filters.text, QueueUp())]
        },
        fallbacks=[MessageHandler(Filters.all, IdleController.error)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    setup_proxy_and_start(TOKEN, True)



