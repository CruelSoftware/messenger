import os
import logging
import logging.handlers

log_format = '%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'


class LogHandler:

    def __init__(self, logger_name: str, filename: str, log_level: int = 3, log_rotation: bool = False):
        self.filename = self.check_log_path(filename)
        if not log_rotation:
            logging.basicConfig(format=log_format, level=log_level, filename=self.filename)
            self.logger = logging.getLogger(logger_name)
        else:
            self.create_rotation_log(logger_name)

        self.logger.level = log_level

    def create_rotation_log(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        handler = logging.handlers.RotatingFileHandler(
            "{}_rotation.log".format(self.filename), maxBytes=2048 * 100 * 100, backupCount=7)
        f = logging.Formatter(log_format)
        handler.setFormatter(f)
        self.logger.addHandler(handler)

    @staticmethod
    def check_log_path(filename):

        log_path = filename.split('\\')
        if len(log_path) == 1:
            log_path = filename.split('/')

        if len(log_path) == 1:
            log_path = os.path.join(os.getcwd(), log_path[0])
            full_path = log_path

        else:
            log_file = log_path.pop()
            log_path = os.path.join(os.getcwd(), *log_path)

            if not os.path.exists(log_path):
                os.makedirs(log_path)
            full_path = os.path.join(log_path, log_file)
        return full_path
