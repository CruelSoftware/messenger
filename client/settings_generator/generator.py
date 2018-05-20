from core import Singleton


class ClientSettingsGenerator(dict, metaclass=Singleton):

    def __init__(self, settings):
        super().__init__()
        _server_settings = getattr(settings, 'CLIENT_SETTINGS', {})
        _server_settings.update({
            'SERVER': _server_settings.get('SERVER', 'localhost'),
            'PORT': _server_settings.get('PORT', '7777'),
        })
        self.update({'CLIENT_SETTINGS': _server_settings})
