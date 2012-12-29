import logging
error_logger = logging.getLogger('errors')

class ExceptionLoggerMiddleware():
    def process_exception(self, request, exception):
        error_logger.error("request {request} threw an exception. \nStacktrace: {stacktrace)".format(
            request = str(request)),
            stacktrace = str(exception)
        )
        return None