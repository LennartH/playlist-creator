import logging


class WithLogger:

    @classmethod
    def logger(cls) -> logging.Logger:
        # TODO Include module name
        return logging.getLogger(cls.__name__)
