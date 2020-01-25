class Feature:
    funcs = {}
    markups = {}

    def __init__(self, entry_state):
        self.state = entry_state

    def enter(self, update, context):
        context.user_data['substate'] = None
        return self.state

    def release(self, update, context):
        context.user_data['substate'] = None
        update.message.reply_text('СТП им. Арташеса, слушаем вас',
                                  reply_markup=self.markups['idle'])
        return 0

    def __call__(self, update, context):
        state = context.user_data.get('substate', None)
        return self.funcs[state](update, context)

    def __getitem__(self, item):
        return self.funcs[item]

    def keys(self):
        return self.funcs.keys()
