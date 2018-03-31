import logging


def get_logger_debug(name):
    logger = logging.getLogger(name)
    if len(logger.handlers) != 0:
        return logger
    hd = logging.FileHandler('scloud.log')
    #hd = logging.handlers.RotatingFileHandler('/var/log/' + name + '.log', maxBytes=512000, backupCount=40)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(filename)s %(lineno)d  %(message)s')
    hd.setFormatter(formatter)
    logger.addHandler(hd)
    logger.setLevel(logging.DEBUG)
    return logger


def get_logger_info(name):
    logger = logging.getLogger(name)
    if len(logger.handlers) != 0:
        return logger
    hd = logging.FileHandler('%s.log' % name)
    logger.addHandler(hd)
    logger.setLevel(logging.INFO)
    return logger


lg = get_logger_info("access_log")


class access_log(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        print(*args, self.f.__name__)
        #argarr = [str(i) for i in args]
        #lg.log(logging.INFO, ",".join(argarr))
        return self.f(*args)


@access_log
def func1(t ,a ,b):
    return a+b


print(func1("test", 1 ,2))