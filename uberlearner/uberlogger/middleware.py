import logging

class ExceptionLoggerMiddleware():
    def process_exception(self, request, exception):
        logger = logging.getLogger('exceptionLoggerMiddleware')
        logger.error("request {request} threw an exception. \nStacktrace: {stacktrace)".format(
            request = str(request)),
            stacktrace = str(exception)
        )
        return None