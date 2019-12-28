from telegram import ReplyKeyboardMarkup


TOKEN = "916090859:AAEugs6uNfvbqq6nnuxk0h57kbfjcn6_T-o"


admins = []
people = {}
path_to_people = 'config/people.cfg'
path_to_admins = 'config/admins.cfg'
path_to_subjects = 'subjects/'
with open(path_to_people, encoding='utf-8') as file:
    for line in file.readlines():
        line = line.split()
        people[int(line[0])] = line[1]
with open(path_to_admins, encoding='utf-8') as file:
    for line in file.readlines():
        admins.append(int(line))


markups = {'idle': ReplyKeyboardMarkup([['Собрать отчёт в PDF',
                                         'Встать в очередь, чтобы задать вопрос'],
                                        ['Панель админ. доступа']],
                                       one_time_keyboard=True,
                                       resize_keyboard=True),
           'admin': ReplyKeyboardMarkup([['Получить архив с отчётами',
                                          'Разослать "письма счастья"']],
                                        one_time_keyboard=False,
                                        resize_keyboard=True),
           'gathering': ReplyKeyboardMarkup([['Конец']],
                                            resize_keyboard=True,
                                            one_time_keyboard=False),
           }
