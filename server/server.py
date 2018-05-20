import json
import socket as s

from logger import LogHandler

from . import settings
from .settings_generator import ServerSettingsGenerator


class Server:

    client = None

    def __init__(self, log_level: (int, str) = 'INFO'):

        self.settings = ServerSettingsGenerator(settings)['SERVER_SETTINGS']
        self.log = LogHandler(logger_name='server', filename='server.log', log_level=log_level)
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        except s.error:
            self.log.logger.error('Failed to create socket')

        self.port = self.socket.bind((self.settings['HOST'], self.settings['PORT']))
        self.socket.listen(self.settings['QUERIES_AMOUNT'])
        self.log.logger.info('Listening for connections on port: {}'.format(self.port))

    def start(self):
        while True:
            self.client, address = self.socket.accept()
            self.log.logger.info('Client {} with ip-address {} connected'.format(client, address))

    def response(self, data):
        if self.client:
            self.client.send(json.dumps(data).encode('utf-8'))
