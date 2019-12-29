from config import admins, people, markups, subjects, path_to_subjects_folder
import config, os
from utility import access, combine_files, add_to_archive

[IDLE,
 COMBINE_GATHERING,
 SUBMIT_GETTING_SUBJECT,
 SUBMIT_GATHERING,
 GETTING_SURNAME,
 COLLECTING_SUBJECT,
 GETTING_LETTER_TYPE,
 GETTING_LETTER_TEXT,
 GETTING_LETTER_SUBJECT] = range(9)


def start(update, context):
    uid = update.message.from_user.id
    context.user_data['is_admin'] = uid in admins
    context.user_data['uid'] = uid
    if uid in people:
        context.user_data['surname'] = people[uid]
    else:
        return request_surname(update, context)
    update.message.reply_text('Пользователь распознан: ' + context.user_data['surname'])
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
                              'среагировать на происходящее.',
                              reply_markup=markups['idle'])
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
def get_file_for_pdf(update, context):
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


@access(admin=False)
def submit_files_to_subject(update, context):
    update.message.reply_text('Выберите имя предмета, отчёт по которому '
                              'вы добавляете.', reply_markup=markups['subjects'])
    return SUBMIT_GETTING_SUBJECT


@access(admin=False)
def get_subject_name_submission(update, context):
    if update.message.text in subjects:
        context.user_data['subject'] = update.message.text
        context.user_data['files'] = []
        update.message.reply_text('Отправьте по очереди все необходимые файлы. '
                                  'Если вы пришлёте несколько файлов, они будут '
                                  'автоматически объединены в ZIP-архив. '
                                  'Повторная попытка отправить файлы по какому-то '
                                  'предмету перезапишет отправленные ранее файлы.',
                                  reply_markup=markups['gathering'])
        return SUBMIT_GATHERING
    else:
        update.message.reply_text('Такого предмета в списке не наблюдается.')
        return SUBMIT_GETTING_SUBJECT


@access(admin=False)
def get_file_submission(update, context):
    if update.message.photo:
        link = update.message.photo[0].get_file()
        file = str(link.download())
        os.rename(file, update.message.document.file_name)
        context.user_data['files'].append(update.message.document.file_name)
        update.message.reply_text('Файл успешно добавлен в список.')
        return SUBMIT_GATHERING
    elif update.message.document:
        link = update.message.document.get_file()
        file = str(link.download())
        os.rename(file, update.message.document.file_name)
        context.user_data['files'].append(update.message.document.file_name)
        update.message.reply_text('Файл успешно добавлен в список.')
        return SUBMIT_GATHERING
    elif update.message.text.lower() == 'конец':
        update.message.reply_text('Начинаю склейку...')
        add_to_archive(*context.user_data['files'],
                       subject=context.user_data['subject'],
                       surname=context.user_data['surname'])
        update.message.reply_text('Готово.',
                                  reply_markup=markups['idle'])
        return IDLE
    else:
        update.message.reply_text('Это не похоже на файл, ты за идиота меня '
                                  'принимаешь?')
        return SUBMIT_GATHERING


@access(admin=True)
def get_submissions(update, context):
    update.message.reply_text('Выберите предмет, отчёты по которому вы желаете собрать.',
                              reply_markup=markups['subjects'])
    return COLLECTING_SUBJECT


@access(admin=True)
def get_collecting_subject(update, context):
    if update.message.text in subjects:
        if subjects[update.message.text]:
            with open(path_to_subjects_folder + update.message.text + '.zip',
                      mode='rb') as file:
                update.message.reply_text('Получите-распишитесь:',
                                          reply_markup=markups['idle'])
                update.message.reply_document(file)
        else:
            update.message.reply_text('Холопы ещё не прислали ни единого отчёта по '
                                      'выбранному предмету. Советуем разослать '
                                      '"письма счастья", ваше величество.',
                                      reply_markup=markups['idle'])
        return IDLE
    else:
        update.message.reply_text('Такого предмета в наших списках не наблюдается.')
        return COLLECTING_SUBJECT


@access(admin=True)
def show_admin_panel(update, context):
    update.message.reply_text('Пожалуйста.', reply_markup=markups['admin'])
    return IDLE


@access(admin=True)
def send_angry_letter(update, context):
    update.message.reply_text('По какому предмету вы желаете потребовать отчёты?',
                              reply_markup=markups['subjects'])
    return GETTING_LETTER_SUBJECT


@access(admin=True)
def request_letter_type(update, context):
    if update.message.text in subjects:
        context.user_data['subject'] = update.message.text
        update.message.reply_text('Какие письма вы хотите разослать плебеям? Можно '
                                  'разослать шаблонные, а можно отправить гонца с '
                                  'посланием, сформулированным лично вами.',
                                  reply_markup=markups['letter_type_choice'])
        return GETTING_LETTER_TYPE
    else:
        update.message.reply_text('Ваше величество, вы ничего не путаете? В нашей базе '
                                  'нет такого предмета.')
        return GETTING_LETTER_SUBJECT


@access(admin=True)
def get_letter_type(update, context):
    if update.message.text == 'Шаблонные':
        update.message.reply_text('Начинаю рассылку.')
        sent = []
        for uid, surname in people.items():
            if surname not in subjects[context.user_data['subject']]:
                message = 'Где отчёты по предмету "{}", ' \
                          'Лебов... кхм, то есть {}?'.format(context.user_data['subject'], surname)
                update.message.bot.send_message(uid, message)
                sent.append(surname)
        update.message.reply_text('Успешно отправлены письма следующим людям:\n' + '\n'.join(sent),
                                  reply_markup=markups['idle'])
        return IDLE
    elif update.message.text == 'Написать своё':
        update.message.reply_text('Введите текст гневного письма для рассылки.')
        return GETTING_LETTER_TEXT
    else:
        update.message.reply_text('Я не понимаю, что вы имеете ввиду, воспользуйтесь '
                                  'клавиатурой с вариантами ответа.',
                                  reply_markup=markups['subjects'])
        return GETTING_LETTER_TYPE


@access(admin=True)
def get_letter_text(update, context):
    update.message.reply_text('Начинаю рассылку.')
    sent = []
    for uid, surname in people.items():
        if surname not in subjects[context.user_data['subject']]:
            message = update.message.text
            update.message.bot.send_message(uid, message)
            sent.append(surname)
    update.message.reply_text('Успешно отправлены письма следующим людям:\n' + '\n'.join(sent),
                              reply_markup=markups['idle'])
    return IDLE
