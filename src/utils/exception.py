'''
Created on Oct 4, 2014
@author: Mohsen Alimomeni
'''

from __future__ import print_function
import traceback
import inspect
import sys
import os
import logging
import config as conf


def get_logger(name=conf.MAIN_LOGGER):
    logger = logging.getLogger(name)
    if len(logger.handlers) != 0:
        return logger
    # TODO Mohsen, add the path to setting or store it in database
    hd = logging.FileHandler('scloud.log')
    #hd = logging.handlers.RotatingFileHandler('/var/log/' + name + '.log', maxBytes=512000, backupCount=40)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(filename)s %(lineno)d  %(message)s')
    hd.setFormatter(formatter)
    logger.addHandler(hd)
    logger.setLevel(logging.DEBUG)
    return logger


def show_frame(a=0, b=3):
    ret = ""
    for num in range(a, b):
        frame = sys._getframe(num)
        ret += str(num-a)
        ret += "\n  frame     = %s" % num
        ret += "\n  function  = %s()" % frame.f_code.co_name
        ret += "\n  file/line = %s:%s" % (frame.f_code.co_filename, frame.f_lineno)
    return ret


class Printer:
    """
        Fake logger class to print to screen
    """
    @classmethod
    def info(cls, text):
        print(text)

    @classmethod
    def error(cls, text):
        print(text, file=sys.stderr)

    @classmethod
    def debug(cls, text):
        print(text)


def debug_log(e_str, show=conf.DEBUG, tag=""):
    """
    :param show: controls showing in "console"
    """
    if show:
        func = inspect.currentframe().f_back.f_code
        filename = os.path.basename(func.co_filename)
        line_num, func_name = func.co_firstlineno, func.co_name
        location = "{}-{}-{}:{}".format(tag.encode('utf-8'), filename.encode('utf-8'), func_name, line_num)
        error_log(e_str, priority=conf.LEVELS.DEBUG, show=False, location=location)


# TODO @Mohsen check if you agree with the changes
def error_log(e, priority=conf.LEVELS.ERROR, show=False, location=""):
    """
        Logs the stack frames for the exception raised
    """
    if priority < conf.PRIORTY:
        return True
    if conf.TESTMODE:
        logger = Printer
    else:
        try:
            logger = get_logger(conf.MAIN_LOGGER)
        except Exception as e:
            logger = Printer

    msg = "Unknown Message"
    code = -1
    if e is None:
        return code

    if location == "":
        func = inspect.currentframe().f_back.f_code
        filename = os.path.basename(func.co_filename)
        line_num, func_name = func.co_firstlineno, func.co_name
        location = "{}-{}:{}".format(filename, func_name, line_num)
    etype = type(e).__name__
    if isinstance(e, str) or isinstance(e, unicode):
        msg = e
        etype = ""
    elif isinstance(e, SCException):
        if conf.EXPDISABLED:
            raise
        msg = traceback.format_exc()
    elif isinstance(e, Exception):
        if conf.EXPDISABLED:
            raise
        msg = traceback.format_exc()
    msg = "({}-{}): {}".format(etype, location, msg.encode('utf-8'))

    if priority == conf.LEVELS.INFO:
        logger.info(msg)
    elif priority == conf.LEVELS.DEBUG:
        logger.debug(msg)
    else:
        logger.error(msg)
    return True