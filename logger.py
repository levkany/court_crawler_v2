import logging
import os
import sys
import json

# Get the current script directory
current_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(current_directory, 'log.txt')

# Custom JSON Formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_message = {
            'level': record.levelname,
            'message': record.getMessage(),
            'time': self.formatTime(record, self.datefmt)
        }
        return json.dumps(log_message)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a logger
logger = logging.getLogger('crawler')

# Create a file handler
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)

# Create a JSON formatter and set it for the file handler
json_formatter = JsonFormatter()
file_handler.setFormatter(json_formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Redirect stdout and stderr to the logger
class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)
