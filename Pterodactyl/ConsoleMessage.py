# -----------------------------------------------------------------------------
# File Name   : ConsoleMessage.py
# Description : Defines the ConsoleMessage class for logging messages to both
#               the console (with colored output) and a log file. Useful for
#               debugging and structured logging in CLI-based Python tools.
#
# Author      : X
# Created On  : 05/08/2025
# Last Updated: 05/08/2025
# -----------------------------------------------------------------------------

import logging
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

class ConsoleMessage:
    def __init__(self, log_file: str = "ConsoleMessage.log"):
        self.logger = logging.getLogger("ConsoleMessage")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            file_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s %(message)s',
                                               datefmt='%Y-%m-%d %H:%M:%S')

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(self.ColorFormatter())

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    class ColorFormatter(logging.Formatter):
        def format(self, record):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = record.getMessage()

            color_map = {
                "INFO": Fore.BLUE,
                "DEBUG": Fore.CYAN,
                "WARNING": Fore.YELLOW,
                "ERROR": Fore.RED,
            }

            color = color_map.get(record.levelname, "")
            level_colored = f"{color}{record.levelname:<8}{Style.RESET_ALL}"

            return f"{timestamp} {level_colored} Petro {message}"

    def info(self, msg): self.logger.info(msg)
    def debug(self, msg): self.logger.debug(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
# -----------------------------------------------------------------------------
# End of File: ConsoleMessage.py
# -----------------------------------------------------------------------------
