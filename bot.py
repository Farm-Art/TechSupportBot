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
        entry_points=[CommandHandler('start', start)],
        states={
            IDLE: [MessageHandler(Filters.regex('^Собрать отчёт в PDF$'),
                                  combine_pdfs),
                   MessageHandler(Filters.regex('^Отправить отчёт вышестоящим '
                                                'инстанциям$'),
                                  submit_files_to_subject),
                   MessageHandler(Filters.regex('^Получить архив с отчётами$'),
                                  get_submissions),
                   MessageHandler(Filters.regex('^Панель админ. доступа$'),
                                  show_admin_panel),
                   MessageHandler(Filters.regex('^Разослать "письма счастья"$'),
                                  send_angry_letter),
                   MessageHandler(Filters.regex('^Встать в очередь$'),
                                  put_in_queue),
                   MessageHandler(Filters.regex('^Выйти из очереди$'),
                                  remove_from_queue),
                   MessageHandler(Filters.regex('^Следующий$'),
                                  tell_next),
                   MessageHandler(Filters.regex('^Послушать музыку$'),
                                  get_music),
                   CommandHandler('start', start)],
            COMBINE_GATHERING: [MessageHandler(Filters.all, get_file_for_pdf)],
            GETTING_SURNAME: [MessageHandler(Filters.text, store_surname)],
            SUBMIT_GATHERING: [MessageHandler(Filters.all, get_file_submission)],
            SUBMIT_GETTING_SUBJECT: [MessageHandler(Filters.text, get_subject_name_submission)],
            COLLECTING_SUBJECT: [MessageHandler(Filters.text, get_collecting_subject)],
            GETTING_LETTER_SUBJECT: [MessageHandler(Filters.text, request_letter_type)],
            GETTING_LETTER_TYPE: [MessageHandler(Filters.text, get_letter_type)],
            GETTING_LETTER_TEXT: [MessageHandler(Filters.text, get_letter_text)]
        },
        fallbacks=[MessageHandler(Filters.all, error)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    setup_proxy_and_start(TOKEN, True)
