import logging


class LogHandler:

    def __init__(self, logger_name, filename, log_level=logging.ERROR):

        logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                            level=log_level, filename=filename)
        self.logger = logging.getLogger(logger_name)