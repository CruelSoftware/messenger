import socket as s

from logger import LogHandler


class Server:

    def __init__(self, log_level='INFO'):

        self.log = LogHandler(logger_name='server', filename='server.log', log_level=log_level)
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        except s.error:
            self.log.logger.error('Failed to create socket')

        self.port = self.socket.bind(('', 7777))
        self.socket.listen(10)
        self.log.logger.info('Listening for connections on port: {}'.format(self.port))

    def start(self):
        while True:
            client, address = self.socket.accept()
            self.log.logger.info('Client {} with ip-address {} connected'.format(client, address))