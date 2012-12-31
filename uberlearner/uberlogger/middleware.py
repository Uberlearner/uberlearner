from . import logger

class ExceptionLoggerMiddleware():
    def process_exception(self, request, exception):
        logger.error("request {request} threw an exception. \nStacktrace: {stacktrace)".format(
            request = str(request)),
            stacktrace = str(exception)
        )
        return None