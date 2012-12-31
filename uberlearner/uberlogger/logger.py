import hoover
from django.conf import settings
import logging

class Logger():
    def __init__(self):
        self.handler = hoover.LogglyHttpHandler(token=settings.LOGGLY_TOKEN)
        self.log = logging.getLogger('Uberlearner')
        self.log.addHandler(self.handler)
        self.log.setLevel(logging.INFO)

    def info(self, message):
        self.log.info(message)

    def error(self, message):
        self.log.error(message)

    def warn(self, message):
        self.log.warn(message)

    def debug(self, message):
        self.log.debug(message)