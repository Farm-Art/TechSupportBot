from config import admins, people, markups
import config, os
from utility import access, combine_files

IDLE, \
COMBINE_GATHERING, \
SUBMIT_GETTING_SUBJECT, \
SUBMIT_GETTING_FILE, \
GETTING_SURNAME = range(5)


def start(update, context):
    uid = update.message.from_user.id
    context.user_data['is_admin'] = uid in admins
    context.user_data['uid'] = uid
    if uid in people:
        context.user_data['surname'] = people[uid]
    else:
        return request_surname(update, context)
    update.message.reply_text('Пользователь распознан: {}'.format(context.user_data['surname']))
    if context.user_data['is_admin']:
        update.message.reply_text('Доброго дня, ваше величество, система распознала '
                                  'в вас администратора.',
                                  reply_markup=markups['idle'])
    else:
        update.message.reply_text('СТП им. Арташеса, слушаем вас.',
                                  reply_markup=markups['idle'])
    return IDLE


def error(update, context):
    update.message.reply_text('Произошёл троллинг, и бот не смог адекватно '
                              'среагировать на происходящее.')
    return IDLE


@access(admin=False)
def request_surname(update, context):
    update.message.reply_text('Видимо, вы пользуетесь этим ботом впервые. '
                              'Для продолжения использования, введите '
                              'вашу фамилию - мы запишем её в паре с вашим '
                              'Telegram UID для, например, дальнейшей '
                              'подстановки в имена файлов.')
    return GETTING_SURNAME


@access(admin=False)
def store_surname(update, context):
    surname = update.message.text.capitalize()
    with open(config.path_to_people, mode='a', encoding='utf-8') as file:
        print(context.user_data['uid'], surname,
              file=file)
        people[context.user_data['uid']] = surname
        context.user_data['surname'] = surname
        file.close()
    update.message.reply_text('Вы были успешно занесены в список.',
                              reply_markup=markups['idle'])
    return IDLE


@access(admin=True)
def combine_pdfs(update, context):
    context.user_data['files'] = []
    update.message.reply_text('Отправьте файлы в порядке склейки. '
                              'Бот принимает файлы .pdf, .jpg, .png, '
                              '.docx и .doc.',
                              reply_markup=markups['gathering'])
    return COMBINE_GATHERING


@access(admin=False)
def get_file(update, context):
    if update.message.photo:
        link = update.message.photo[0].get_file()
        if any(link.file_path.endswith(ext) for ext in ['.jpg', '.png']):
            file = str(link.download())
            context.user_data['files'].append(file)
            update.message.reply_text('Файл успешно добавлен в список '
                                      'на склейку.')
        else:
            update.message.reply_text('Некорректное расширение файла. '
                                      'Файл пропущен, процесс склейки ещё '
                                      'активен.')
    elif update.message.document:
        link = update.message.document.get_file()
        if any(link.file_path.endswith(ext) for ext in ['.jpg', '.png', '.doc',
                                                        '.docx', '.pdf']):
            file = str(link.download())
            context.user_data['files'].append(file)
            update.message.reply_text('Файл успешно добавлен в список '
                                      'на склейку.')
        else:
            update.message.reply_text('Некорректное расширение файла. '
                                      'Файл пропущен, процесс склейки ещё '
                                      'активен.')
    elif update.message.text.lower() == 'конец':
        update.message.reply_text('Начинаю склейку...')
        path = combine_files(*context.user_data['files'],
                             name=context.user_data['surname'])
        with open(path, mode='rb') as file:
            update.message.reply_document(file, reply_markup=markups['idle'])
            file.close()
        os.remove(path)
        return IDLE
    else:
        update.message.reply_text('Было бы здорово, если бы вы прислали файл.')
    return COMBINE_GATHERING

