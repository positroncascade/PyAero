import sys
from PyQt4 import QtGui, QtCore
import logging


"""
Customized logger module which handles stdout and stderr.
Log messages are either plain strings or can be in HTML format.

Example:
import PLogger as logger
logger.log.info('This is a plain log message.')
logger.log.info(
    'This is a <b><font color="#2784CB">HTML customized</b> message.')
"""


class LogStream(QtCore.QObject):
    _stdout = None
    _stderr = None
    messageWritten = QtCore.pyqtSignal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if (not self.signalsBlocked()):
            self.messageWritten.emit(unicode(msg))

    @staticmethod
    def stdout():
        if (not LogStream._stdout):
            LogStream._stdout = LogStream()
            sys.stdout = LogStream._stdout
        return LogStream._stdout

    @staticmethod
    def stderr():
        if (not LogStream._stderr):
            LogStream._stderr = LogStream()
            sys.stderr = LogStream._stderr
        return LogStream._stderr


class LogHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        # add HTML newline here because we write HTML strings with this logger
        newline = '<br>'
        if record:
            LogStream.stdout().write('%s%s' % (record, newline))


log = logging.getLogger(__name__)
handler = LogHandler()
handler.setFormatter(logging.Formatter('[%(levelname)s] - %(message)s'))
log.addHandler(handler)
log.setLevel(logging.DEBUG)
