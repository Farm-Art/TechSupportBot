TOKEN = "916090859:AAHHBksYTGUg4C2IR7nJv4WPkd_BFNMSAFo"

music_tracks = ['Bot Queue Music/{}'.format(i) for i in ('Elevator Music A.mp3',
                                                         'Elevator Music B.mp3',
                                                         'It Hates Me So Much Extended.mp3',
                                                         'Seduce Me.mp3',
                                                         'TF2 Upgrade Station.mp3',
                                                         'KONGOS - Push.mp3',
                                                         'KONGOS - Fools.mp3')]
admins = []
users = {}
subjects = {}
queue = []
path_to_users = 'config/users.cfg'
path_to_admins = 'config/admins.cfg'
path_to_subjects = 'config/subjects.cfg'
path_to_subjects_folder = 'subjects/'
with open(path_to_users, encoding='utf-8') as file:
    for line in file.readlines():
        line = line.split()
        users[int(line[0])] = line[1]
with open(path_to_admins, encoding='utf-8') as file:
    for line in file.readlines():
        admins.append(int(line))
with open(path_to_subjects, encoding='utf-8') as file:
    for line in file.readlines():
        line = line.split()
        namelen = int(line[0])
        subjects[' '.join(line[1:namelen+1])] = line[namelen+1:]
