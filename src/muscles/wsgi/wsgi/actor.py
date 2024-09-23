

class Actor:

    _instances = {}
    _loaders = []

    def __new__(cls, *args, token=None, **kwargs):
        """ Singleton """
        if token not in cls._instances:
            cls._instances[token] = super(Actor, cls).__new__(cls, *args, **kwargs)
            actor = None
            for func in cls._instances[token]._loaders:
                if actor is None:
                    actor = func(token, **kwargs)
        return cls._instances[token]

    def __init__(self, token=None, **kwargs):
        setattr(self, 'token', token)
        for prop, val in kwargs.items():
            setattr(self, prop, val)

    @staticmethod
    def instance(token):
        actor = Actor(token=token)
        return actor

    def loader(self):
        def decorator(func):
            self._loaders.append(func)
        return decorator

    def rules(self):
        pass

    def validate(self):
        pass

    def has_access(self):
        pass

    def is_system(self):
        pass

    def is_robot(self):
        pass

    def is_user(self):
        pass

    def is_guest(self):
        pass