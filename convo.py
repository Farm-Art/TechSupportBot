from telegram import ReplyKeyboardMarkup
from config import admins, users, queue, music_tracks
import config, random
from framework import Feature
from telegram import ChatAction


def access_error(update, context, state):
    update.message.reply_text('У вас недостаточно прав для '
                              'использования этой команды.',
                              reply_markup=IdleController.markups['idle'])
    return state


def access(admin=True, state=0):
    def wrapper(func):
        def result(self, update, context):
            if admin:
                if context.user_data['is_admin']:
                    return func(self, update, context)
                else:
                    return access_error(update, context, state)
            else:
                return func(self, update, context)
        return result
    return wrapper


def set_state(context, state):
    context.user_data['substate'] = state


class IdleController(Feature):
    [
     IDLE,
     REGISTER,
     QUEUE
    ] = range(3)

    markups = {
        'idle': ReplyKeyboardMarkup([['Взаимодействие с очередью']]),
    }

    def __init__(self, entry_state):
        super().__init__(entry_state)
        self.funcs = {
            None: self.switch,
            'switching': self.switch
        }
        self.features = {
            'взаимодействие с очередью': QueueUp()
        }

    def start(self, update, context):
        context.user_data['uid'] = update.message.from_user.id
        if context.user_data['uid'] not in users:
            return RegisterSurname().enter(update, context)
        if context.user_data['uid'] in admins:
            update.message.reply_text('Система почувствовала в вас королевскую '
                                      'кровь. Доброго дня, ваше величество.',
                                      reply_markup=self.markups['idle'])
        else:
            update.message.reply_text('Добрый день, СТП слушает вас.',
                                      reply_markup=self.markups['idle'])
        context.user_data['surname'] = users[context.user_data['uid']]
        context.user_data['is_admin'] = context.user_data['uid'] in admins
        set_state(context, None)
        return self.IDLE

    def switch(self, update, context):
        if update.message.text.lower() in self.features:
            set_state(context, None)
            return self.features[update.message.text.lower()](update, context)
        update.message.reply_text('Такой команды я не знаю, извиняйте')
        return self.IDLE

    def error(self, update, context):
        update.message.reply_text('Произошёл троллинг.')
        set_state(context, None)
        return self.IDLE


class RegisterSurname(Feature):
    state = IdleController.REGISTER
    markups = {
        'idle': IdleController.markups['idle']
    }

    def __init__(self):
        super().__init__(self.state)
        self.enter = self.request
        self.funcs = {
            None: self.request,
            'requesting surname': self.store
        }

    def request(self, update, context):
        update.message.reply_text('Похоже, что вы ещё не зарегистрированы '
                                  'в нашей системе. Для продолжения работы '
                                  'с ботом, введите свою фамилию. Мы запишем '
                                  'её вместе с вашим Telegram UID для '
                                  'дальнейшей идентификации и таких процедур, '
                                  'как автоматическая подпись отчётов.')
        set_state(context, 'requesting surname')
        return self.state

    def store(self, update, context):
        surname = update.message.text.capitalize()
        with open(config.path_to_users, mode='a', encoding='utf-8') as file:
            print(context.user_data['uid'], surname,
                  file=file)
            users[context.user_data['uid']] = surname
            context.user_data['surname'] = surname
            file.close()
        update.message.reply_text('Успешно добавлен пользователь с UID={} и '
                                  'фамилией={}'.format(context.user_data['uid'],
                                                       update.message.text.capitalize()))
        return self.release(update, context)


class QueueUp(Feature):
    markups = {
        'menu': ReplyKeyboardMarkup([['Встать в очередь', 'Выйти из очереди'],
                                     ['Положение в очереди', 'Послушать музыку'],
                                     ['Вернуться в главное меню']],
                                    one_time_keyboard=False,
                                    resize_keyboard=True),
        'idle': IdleController.markups['idle']
    }
    state = IdleController.QUEUE

    def __init__(self):
        super().__init__(IdleController.QUEUE)
        self.funcs = {
            None: self.enter,
            'choosing': self.switcher,
            'встать в очередь': self.put_in_queue,
            'выйти из очереди': self.pop_from_queue,
            'положение в очереди': self.tell_queue_pos,
            'послушать музыку': self.send_music,
            'next': self.next,
            'view': self.view,
            'вернуться в главное меню': self.release,
        }

    def enter(self, update, context):
        update.message.reply_text('Что именно вы хотите сделать?',
                                  reply_markup=self.markups['menu'])
        set_state(context, 'choosing')
        return self.state

    def switcher(self, update, context):
        msg = update.message.text.lower()
        if msg in self.funcs:
            context.user_data['substate'] = msg
            return self(update, context)
        else:
            update.message.reply_text('Я такой команды не знаю :/')
            return self.state

    def put_in_queue(self, update, context):
        uid = context.user_data['uid']
        if uid in queue:
            update.message.reply_text('Вы уже находитесь в очереди.')
            context.user_data['substate'] = 'choosing'
        else:
            queue.append(uid)
            update.message.reply_text('Вы были добавлены в очередь. '
                                      'Ваша позиция - {}'.format(len(queue)))
        set_state(context, 'choosing')
        return self.state

    def pop_from_queue(self, update, context):
        uid = context.user_data['uid']
        if uid in queue:
            queue.remove(uid)
            update.message.reply_text('Вы были успешно удалены из очереди.')
        else:
            update.message.reply_text('Вас не было в очереди!')
        set_state(context, 'choosing')
        return self.state

    def tell_queue_pos(self, update, context):
        uid = context.user_data['uid']
        if uid in queue:
            update.message.reply_text('Ваше положение в '
                                      'очереди - {}'.format(queue.index(uid) + 1))
        else:
            update.message.reply_text('Вас нет в очереди!')
        set_state(context, 'choosing')
        return self.state

    def send_music(self, update, context):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id,
                                     action=ChatAction.UPLOAD_DOCUMENT)
        with open(random.choice(music_tracks), mode='rb') as file:
            update.message.reply_audio(file)
        update.message.reply_text('Наслаждайтесь прослушиванием.')
        set_state(context, 'choosing')
        return self.state

    @access(admin=True, state=state)
    def next(self, update, context):
        if queue:
            uid = queue.pop(0)
            update.message.reply_text('Вызываю {}'.format(users[uid]))
            context.bot.send_message(uid, 'Пришла ваша очередь!')
        else:
            update.message.reply_text('Очередь пуста!')
        set_state(context, 'choosing')
        return self.state

    @access(admin=True, state=state)
    def view(self, update, context):
        update.message.reply_text('В очереди {} человек(а). Вот список:\n{}'.format(
            len(queue), '\n'.join(queue)
        ))
        set_state(context, 'choosing')
        return self.state
