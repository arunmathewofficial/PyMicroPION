import logging
from logging.handlers import RotatingFileHandler

# Define a custom logging level for errors
ERROR_LEVEL = 25  # You can choose any value that is not already in use

# Define a custom formatter for error messages
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[92m',    # White
        'INFO': '\033[0m',     # White
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',   # Red
        'CRITICAL': '\033[91m' # Red
    }

    def format(self, record):
        log_message = super().format(record)
        return self.COLORS.get(record.levelname, '\033[0m') + log_message + '\033[0m'

def setup_logger(name, log_file):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=2)
    file_handler.setFormatter(formatter)

    # Create a stream handler with the colored formatter
    stream_handler = logging.StreamHandler()
    colored_formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(colored_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level=logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)  # Add the stream handler to the logger

    # Add custom error level to the logger
    logging.addLevelName(ERROR_LEVEL, 'ERROR')
    setattr(logger, 'error', lambda message, *args, **kwargs: logger._log(ERROR_LEVEL, message, args, **kwargs))

    return logger

