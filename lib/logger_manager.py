import os

root_dir = os.getcwd().split("RaspiBrain")[0] + "RaspiBrain"

import logging
import colorlog
from datetime import datetime

class LoggerManager:
    """
    Advanced Logger Manager to handle logging with color console output and file logging.
    Supports both colored console logging and file-based logging with timestamps.
    """
    def __init__(self, log_name="log"):
        """
        Initialize the LoggerManager with colored console and file logging.

        Args:
            root_dir (str): Root directory to save logs.
            log_name (str): Base name for the log file.
        """
        # Create logs directory
        log_dir = os.path.join(root_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Generate timestamp and log file path
        timestamp = datetime.now().strftime("%H-%M-%S")
        self.title = f"{log_name}_{timestamp}"
        self.log_path = os.path.join(log_dir, f"{self.title}-logs.txt")

        # Create logger
        self.logger = colorlog.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        # Clear any existing handlers to prevent duplicates
        self.logger.handlers.clear()

        # Colored Console Handler
        console_handler = colorlog.StreamHandler()
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] %(levelname)-8s%(reset)s %(light_black)s%(filename)s:%(lineno)d:%(reset)s %(message)s",
            datefmt="%H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)

        # File Handler
        file_handler = logging.FileHandler(self.log_path)
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(filename)s:%(lineno)d: %(message)s",
            datefmt="%H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def set_level(self, console_level=logging.INFO, file_level=logging.DEBUG):
        """
        Change the logging levels dynamically for console and file handlers.

        Args:
            console_level (int): Logging level for console output.
            file_level (int): Logging level for file output.
        """
        # Update levels for all handlers
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(console_level)
            elif isinstance(handler, logging.FileHandler):
                handler.setLevel(file_level)

    def get_logger(self):
        """
        Return the logger instance.

        Returns:
            logging.Logger: Configured logger instance.
        """
        return self.logger

    def get_title(self):
        """
        Return the log title.

        Returns:
            str: Log file title/name.
        """
        return self.title
