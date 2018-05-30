import json
import select
import socket as s

from logger import resources_log
from logger import LogHandler

from core.status import (
    STATUS_200_OK,
    STATUS_400_BAD_REQUEST,
    STATUS_401_UNAUTHORIZED,
    STATUS_500_INTERNAL_ERROR,
    STATUS_403_NOT_ALLOWED
)

from . import settings
from .settings_generator import ServerSettingsGenerator


class Server:
    address_match = True
    client, clients, clients_requests = None, [], []
    settings = ServerSettingsGenerator(settings)['SERVER_SETTINGS']
    log_level = settings['LOG_LEVEL']
    log = LogHandler(logger_name='server', filename=settings['LOG_FILE_PATH'], log_level=log_level, log_rotation=True)

    def __init__(self, addr: (str, None) = None, port: (int, None) = None):

        self.accept_address = addr
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        except s.error:
            self.log.logger.error('Failed to create socket')

        self.port = port if port else self.settings['PORT']
        self.socket.bind((self.settings['HOST'], self.port))
        self.socket.listen(self.settings['QUERIES_AMOUNT'])
        self.socket.settimeout(self.settings['SOCKET_TIMEOUT'])
        self.log.logger.info('Listening for connections on port: {}'.format(self.port))

    @resources_log
    def start(self):
        while True:
            try:
                self.client, address = self.socket.accept()
                if self.accept_address:
                    self.address_match = self.accept_address == address

            except OSError as e:
                self.log.logger.error("Failed to accept connection: {}".format(str(e)))

            else:
                self.log.logger.info('Client with ip-address {} connected'.format(address))
                self.clients.append(self.client)

            finally:
                wait = 0
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                    self.log.logger.info('пишут: {}'.format(w))
                    self.log.logger.info('читают: {}'.format(r))
                except Exception as e:
                    self.log.logger.info("Клиент отключился".format(str(e)))

                self.clients_requests = self.read_requests(r, self.clients)  # Save clients requests
                self.write_responses(self.clients_requests, w, self.clients)  # Send responses to clients

    @resources_log
    def response(self, data: dict, client):
        self.log.logger.info("Sending response to client {}: {}".format(client, data))
        client.send(json.dumps(data).encode('utf-8'))

    def read_requests(self, r_clients, all_clients):
        responses = {}  # server responses dict

        for sock in r_clients:
            try:
                data = sock.recv(1024).decode('utf-8')
                responses[sock] = data
            except Exception as e:
                self.log.logger.info('Client {} {} disconnected (())'.format(sock.fileno(), sock.getpeername(), str(e)))
                all_clients.remove(sock)

        return responses

    def write_responses(self, requests, w_clients, all_clients):

        for sock in w_clients:
            if sock in requests:
                try:
                    response_data = ResponseHandler(requests[sock], self.address_match).response_data
                    self.response(response_data, sock)
                except Exception as e:  # Socket is available, client disconnected
                    self.log.logger.info('Client {} {} disconnected ({})'.format(sock.fileno(),
                                                                                 sock.getpeername(),
                                                                                 str(e)))
                    sock.close()
                    all_clients.remove(sock)


class ResponseHandler:
    response_data = None
    required_parameters = ['action', 'time', 'type', 'user']
    available_actions = ['presence', 'message']
    settings = ServerSettingsGenerator(settings)['SERVER_SETTINGS']
    log_level = settings['LOG_LEVEL']
    log = LogHandler(logger_name='server', filename=settings['LOG_FILE_PATH'], log_level=log_level, log_rotation=True)

    action_type_mapping = {
        'presence': {'response': STATUS_200_OK, 'alert': 'optional message'},
        'message': {'response': STATUS_200_OK},
    }

    error_type_mapping = {
        STATUS_400_BAD_REQUEST: {"response": STATUS_400_BAD_REQUEST, "error": "Bad request"},
        STATUS_401_UNAUTHORIZED: {"response": STATUS_401_UNAUTHORIZED, "error": "Unauthorized"},
        STATUS_500_INTERNAL_ERROR: {"response": STATUS_500_INTERNAL_ERROR, "error": "Internal server error"},
    }

    def __init__(self, data: str, address_match: bool):
        super().__init__()

        try:
            data = json.loads(data)

            for key in self.required_parameters:
                if key not in data.keys():
                    self.response_data = (self.error_type_mapping[STATUS_400_BAD_REQUEST])
                    break

        except Exception as e:
            self.response_data = {"response": STATUS_500_INTERNAL_ERROR, "error": str(e)}

        if not self.response_data:
            action = data.get('action')
            if not address_match:
                self.response_data = self.error_type_mapping[STATUS_403_NOT_ALLOWED]

            elif not action:
                self.response_data = self.error_type_mapping[STATUS_400_BAD_REQUEST]

            else:
                method_to_call = getattr(self, action)
                self.response_data = method_to_call(action)

    @resources_log
    def presence(self, action):
        return self.action_type_mapping[action]

    @resources_log
    def message(self, action):
        pass
