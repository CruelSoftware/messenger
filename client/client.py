import json
import time
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
        with s.socket(s.AF_INET, s.SOCK_STREAM) as self.socket:
            is_connected = self.connect_to_server(self.addr, self.port)
            if is_connected:
                while True:
                    response = self.send_presence()
                    self.log.logger.info(self.decode_response(response))

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
        return self.socket.recv(16384)

    @resources_log
    def send_presence(self) -> (bytes, bytearray):
        data = {"action": "presence",
                "time": str(time.time()),
                "type": "status",
                "user": {
                    "account_name": self.user
                }
                }
        return self.request(data)
