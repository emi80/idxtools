"""The indexfile package
"""

import logging

__name__ = "idxtools"
__version__ = "0.12.2.dev1"
_log_level = "WARN"

# custom log format
class CustomFormatter(logging.Formatter):

    FORMATS = {
        logging.DEBUG: '[DBG] %(name)s - %(funcName)s - %(message)s',
        logging.WARN: '[WARN] %(msg)s',
        logging.ERROR: '[ERR] %(msg)s',
        logging.INFO: '[INFO] %(msg)s',
        'DEFAULT': '%(msg)s'
    }
    # dbg_time = '%m/%d/%Y %H:%M:%S'


    def __init__(self, fmt="%(msg)s"):
        logging.Formatter.__init__(self, fmt)


    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result


def getLogger(name):
    """Return the logger given the name"""
    logger = logging.getLogger(name)
    logger.handler = []
    return logger


def setLogLevel(level):
    """Set logger loglevel"""
    log.setLevel(getattr(logging, str(level).upper(), 30))

log = logging.getLogger()
log.handler = []
log.propagate = False
setLogLevel(_log_level)

ch = logging.StreamHandler()
fmt = CustomFormatter()
ch.setFormatter(fmt)
log.addHandler(ch)
