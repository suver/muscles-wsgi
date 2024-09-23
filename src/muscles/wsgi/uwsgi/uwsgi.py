

class UwsgiReload:
    """
    Команда перезагрузки UWSGI
    """

    def __init__(self, config={}):
        self.config = config

    def execute(self):
        print('Reloaded UWSGI')
        import uwsgi
        return uwsgi.reload()
