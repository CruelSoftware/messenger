import json
import socket as s

from logger import resources_log
from logger import LogHandler

from core.status import (
    STATUS_200_OK,
    STATUS_400_BAD_REQUEST,
    STATUS_401_UNAUTHORIZED,
    STATUS_500_INTERNAL_ERROR
)

from . import settings
from .settings_generator import ServerSettingsGenerator


class Server:
    client = None
    settings = ServerSettingsGenerator(settings)['SERVER_SETTINGS']
    log_level = settings['LOG_LEVEL']


    def __init__(self, addr: (str, None) = None, port: (int, None) = None):
        self.log = LogHandler(logger_name='server', filename=self.settings['LOG_FILE_PATH'],
                         log_level=self.log_level, log_rotation=True)
        self.accept_address = addr
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        except s.error:
            self.log.logger.error('Failed to create socket')

        self.port = port if port else self.settings['PORT']
        self.socket.bind((self.settings['HOST'], self.port))
        self.socket.listen(self.settings['QUERIES_AMOUNT'])
        self.log.logger.info('Listening for connections on port: {}'.format(self.port))

    @resources_log
    def start(self):
        address_match = True
        while True:
            self.client, address = self.socket.accept()
            if self.accept_address:
                address_match = self.accept_address == address
            data = self.client.recv(16384)
            self.log.logger.info('Client with ip-address {} connected'.format(address))
            response = ResponseHandler(data, address_match)
            self.response(response)
            #self.socket.close()

    @resources_log
    def response(self, data):
        if self.client:
            self.client.send(json.dumps(data).encode('utf-8'))


class ResponseHandler(dict):
    action_type_mapping = {
        'presence': {'response': STATUS_200_OK, 'alert': 'optional message'}
    }

    error_type_mapping = {
        STATUS_400_BAD_REQUEST: {"response": STATUS_400_BAD_REQUEST, "error": "Bad request"},
        STATUS_401_UNAUTHORIZED: {"response": STATUS_401_UNAUTHORIZED, "error": "Unauthorized"},
        STATUS_500_INTERNAL_ERROR: {"response": STATUS_500_INTERNAL_ERROR, "error": "Internal server error"},
    }

    def __init__(self, data: (bytes, bytearray), address_match: bool):
        super().__init__()

        try:
            data = json.loads(data.decode('utf-8'))
            action = data.get('action')

            if not address_match:
                self.update(self.error_type_mapping[STATUS_401_UNAUTHORIZED])

            elif not action:
                self.update(self.error_type_mapping[STATUS_400_BAD_REQUEST])

            else:
                self.update(self.action_type_mapping[action])

        except Exception as e:
            self.update({"response": STATUS_500_INTERNAL_ERROR, "error": str(e)})
