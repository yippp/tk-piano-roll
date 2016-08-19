class Observer(object):

    def __init__(self, callable, knowledge):
        self.callable = callable
        self.knowledge = knowledge

    def __call__(self, *args, **kwargs):
        self.callable(*args, **kwargs)