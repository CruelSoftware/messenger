from core import get_class_that_defined_method

from .logger import LogHandler


def resources_log(f):
    def wrapper(*args, **kwargs):
        log_instance = None
        _class = get_class_that_defined_method(f)

        if _class:
            for method in _class.__dict__:
                if isinstance(method, LogHandler):
                    log_instance = method

        if not log_instance:
            log_instance = LogHandler(logger_name='common', filename='common.log', log_level=3)

        log_instance.logger.info(r"Function/method name: {}".format(f.__name__))
        log_instance.logger.info('Arguments: {}'.format(args))
        log_instance.logger.info('Keyword arguments:'.format(kwargs))
        result = f(*args, **kwargs)
        return result

    return wrapper

