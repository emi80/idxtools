"""The indexfile package

"""

import logging

__name__ = "idxtools"
__version__ = "0.9"
_log_level = 30


def getLogger(name):
    logger = logging.getLogger(name)
    logger.handler = []
    return logger

def setLogLevel(level):
    log.setLevel(getattr(logging, str(level).upper(), 30))

log = logging.getLogger()
log.handler = []
log.propagate = False
setLogLevel(_log_level)

ch = logging.StreamHandler()
fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(fmt)
log.addHandler(ch)

