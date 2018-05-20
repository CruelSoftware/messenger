import json
import datetime
import socket as s

from logger import LogHandler
from .settings_generator import ClientSettingsGenerator
from . import settings


class Client:

    def __init__(self, server: (str, None) = None, port: (int, None) = None, log_level: (int, str) = 'INFO'):

        self.settings = ClientSettingsGenerator(settings)['CLIENT_SETTINGS']
        self.log = LogHandler(logger_name='server', filename='server.log', log_level=log_level)
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        except s.error:
            self.log.logger.error('Failed to create socket')

        if not server:
            server = self.settings['SERVER']

        if not port:
            port = self.settings['PORT']

        self.connect_to_server(server, port)
        response = self.send_presence()
        self.log.logger.info(self.decode_response(response))

    def connect_to_server(self, server: str, port: int):
        try:
            self.socket.connect((server, port))
        except s.error:
            self.log.logger.error('Failed to connect to server {} on port {}').format()

    @staticmethod
    def decode_response(data: (bytes, bytearray)) -> (dict, list):
        return json.loads(data.decode('itf-8'))

    def request(self, data: (dict, list)) -> (bytes, bytearray):
        return self.socket.send(data=json.dumps(data).encode('utf-8'))

    def send_presence(self) -> (bytes, bytearray):
        data = {"action": "presence", "time": datetime.datetime.utcnow(), "type": "status"}
        return self.request(data)
