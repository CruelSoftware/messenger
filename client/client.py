import json
import datetime
import socket as s

from logger import LogHandler
from .settings_generator import ClientSettingsGenerator
from . import settings


class Client:

    def __init__(self, addr: (str, None) = None, port: (int, None) = None, log_level: (int, None) = None):

        self.settings = ClientSettingsGenerator(settings)['CLIENT_SETTINGS']
        if not log_level:
            log_level = self.settings['LOG_LEVEL']

        self.log = LogHandler(logger_name='client', filename='client.log', log_level=log_level)
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        except s.error:
            self.log.logger.error('Failed to create socket')

        if not addr:
            self.addr = self.settings['SERVER']

        if not port:
            self.port = self.settings['PORT']

    def start(self):
        self.connect_to_server(self.addr, self.port)
        response = self.send_presence()
        self.log.logger.info(self.decode_response(response))
        self.socket.close()

    def connect_to_server(self, server: str, port: int):
        try:
            self.socket.connect((server, port))
        except (s.error, ConnectionRefusedError):
            self.log.logger.error('Failed to connect to server {} on port {}').format(server, port)

    @staticmethod
    def decode_response(data: (bytes, bytearray)) -> (dict, list):
        return json.loads(data.decode('utf-8'))

    def request(self, data: (dict, list)) -> (bytes, bytearray):
        self.socket.send(json.dumps(data).encode('utf-8'))
        return self.socket.recv(16384)

    def send_presence(self) -> (bytes, bytearray):
        data = {"action": "presence", "time": str(datetime.datetime.utcnow()), "type": "status"}
        return self.request(data)
