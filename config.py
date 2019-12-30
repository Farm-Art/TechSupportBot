from telegram import ReplyKeyboardMarkup


TOKEN = "TOKEN"

music_tracks = ['Bot Queue Music/{}'.format(i) for i in ('Elevator Music A.mp3',
                                                         'Elevator Music B.mp3',
                                                         # 'It Hates Me So Much Extended.mp3',
                                                         # 'Seduce Me.mp3',
                                                         'TF2 Upgrade Station.mp3')]
admins = []
people = {}
subjects = {}
queue = []
path_to_people = 'config/people.cfg'
path_to_admins = 'config/admins.cfg'
path_to_subjects = 'config/subjects.cfg'
path_to_subjects_folder = 'subjects/'
with open(path_to_people, encoding='utf-8') as file:
    for line in file.readlines():
        line = line.split()
        people[int(line[0])] = line[1]
with open(path_to_admins, encoding='utf-8') as file:
    for line in file.readlines():
        admins.append(int(line))
with open(path_to_subjects, encoding='utf-8') as file:
    for line in file.readlines():
        line = line.split()
        namelen = int(line[0])
        subjects[' '.join(line[1:namelen+1])] = line[namelen+1:]


markups = {'idle': ReplyKeyboardMarkup([['Собрать отчёт в PDF',
                                         'Отправить отчёт вышестоящим инстанциям'],
                                        ['Встать в очередь',
                                         'Выйти из очереди',
                                         'Послушать музыку'],
                                        ['Панель админ. доступа']],
                                       one_time_keyboard=True,
                                       resize_keyboard=True),
           'admin': ReplyKeyboardMarkup([['Получить архив с отчётами',
                                          'Разослать "письма счастья"'],
                                         ['Следующий']],
                                        one_time_keyboard=True,
                                        resize_keyboard=True),
           'gathering': ReplyKeyboardMarkup([['Конец']],
                                            resize_keyboard=True,
                                            one_time_keyboard=False),
           'subjects': ReplyKeyboardMarkup([[subject] for subject in subjects],
                                           resize_keyboard=True,
                                           one_time_keyboard=False),
           'letter_type_choice': ReplyKeyboardMarkup([['Шаблонные', 'Написать своё']],
                                                     resize_keyboard=True,
                                                     one_time_keyboard=False)
           }
