import json
import socket as s

from logger import LogHandler
from logger import resources_log
from .settings_generator import ClientSettingsGenerator
from . import settings


class Client:
    client, socket = None, None
    settings = ClientSettingsGenerator(settings)['CLIENT_SETTINGS']
    log_level = settings['LOG_LEVEL']
    log = LogHandler(logger_name='client', filename=settings['LOG_FILE_PATH'], log_level=log_level)

    def __init__(self, addr: (str, None) = None, port: (int, None) = None, user: str = settings['DEFAULT_USER']):

        self.user = user

        if not addr:
            self.addr = self.settings['SERVER']

        if not port:
            self.port = self.settings['PORT']

    @resources_log
    def start(self):
        send_presence = True
        with s.socket(s.AF_INET, s.SOCK_STREAM) as self.socket:
            is_connected = self.connect_to_server(self.addr, self.port)
            if is_connected:
                while True:
                    if send_presence:
                        response = self.decode_response(self.send_presence())
                        if int(str(response.get('response'))[0]) != 2:
                            self.log.logger.error('Wrong server response: {}'.format(response))
                            break
                        send_presence = False
                        self.log.logger.info(response)

                    message = input('Enter your message: ')
                    if message == 'exit':
                        break
                    response = self.decode_response(self.send_message(message=message))
                    print('Response: {}'.format(response))

    @resources_log
    def connect_to_server(self, server: str, port: int):
        try:
            self.socket.connect((server, port))
            return True
        except (s.error, ConnectionRefusedError):
            self.log.logger.error('Failed to connect to server {} on port {}'.format(server, port))
            return False

    @staticmethod
    @resources_log
    def decode_response(data: (bytes, bytearray)) -> (dict, list):
        try:
            response = json.loads(data.decode('utf-8'))
            return response
        except json.JSONDecodeError as e:
            return "Failed to parse response: {}".format(str(e))

    @resources_log
    def request(self, data: (dict, list)) -> (bytes, bytearray):
        self.socket.send(json.dumps(data).encode('utf-8'))
        return self.socket.recv(2048)

    @resources_log
    def send_presence(self) -> (bytes, bytearray):
        kwargs = {'user': {"account_name": self.user}, 'type':'status'}
        data = RequestHandler(action='presence', **kwargs)
        return self.request(data)

    @resources_log
    def send_message(self, message: str, to: str = 'Guest') -> (bytes, bytearray):
        kwargs = {'to': to, 'from': self.user, 'encoding': 'utf-8', 'message': message}
        data = RequestHandler(action='msg', **kwargs)
        return self.request(data)


class RequestHandler(dict):

    settings = ClientSettingsGenerator(settings)
    client_settings = settings['CLIENT_SETTINGS']

    log_level = client_settings['LOG_LEVEL']
    log = LogHandler(logger_name='client', filename=client_settings['LOG_FILE_PATH'], log_level=log_level)

    def __init__(self, action, **kwargs):
        super().__init__()
        method_to_call = None

        self.update(self.settings['TEMPLATE_SETTINGS'])

        try:
            method_to_call = getattr(self, action)
        except AttributeError:
            self.log.logger.error('ERROR: wrong action {}'.format(action))

        if method_to_call:
            method_to_call(action, **kwargs)

    @resources_log
    def presence(self, action, **kwargs):
        self.update({"action": action, **kwargs})

    @resources_log
    def msg(self, action: str, **kwargs):
        self.update({"action": action, **kwargs})
