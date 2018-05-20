import socket

from core import Singleton


class ServerSettingsGenerator(dict, metaclass=Singleton):

    def __init__(self, settings):
        super().__init__()
        _server_settings = getattr(settings, 'SERVER_SETTINGS', {})
        _server_settings.update({
            'HOST': _server_settings.get('HOST', self.hostname),
            'PORT': _server_settings.get('PORT', '7777'),
            'QUERIES_AMOUNT': int(_server_settings.get('QUERIES_AMOUNT', 10)),
            'LOG_LEVEL': _server_settings.get('LOG_LEVEL', 4),
        })
        self.update({'SERVER_SETTINGS': _server_settings})

    @property
    def hostname(self):
        return socket.gethostname()
