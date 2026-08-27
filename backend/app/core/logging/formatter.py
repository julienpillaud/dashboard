import logging

MAX_LENGTH = 35
COLORS_MAPPING: dict[str, str] = {
    "DEBUG": "\033[34m",  # blue
    "INFO": "\033[36m",  # cyan
    "WARNING": "\033[33m",  # yellow
    "ERROR": "\033[31m",  # red
    "CRITICAL": "\033[35m",  # magenta
}
RESET_COLOR = "\033[0m"
PROJECT_LOGGER_NAME = "app"


class ColoredFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(
            fmt=f"%(asctime)s [%(levelname)8s] %(name){MAX_LENGTH}s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        color = self._get_color(record)
        self._strip_record_name(record)
        message = super().format(record)
        return f"{color}{message}{RESET_COLOR}"

    def _get_color(self, record: logging.LogRecord) -> str:
        if not record.name.startswith(PROJECT_LOGGER_NAME):
            return "\033[37m"  # light gray
        return COLORS_MAPPING.get(record.levelname, RESET_COLOR)

    @staticmethod
    def _strip_record_name(record: logging.LogRecord) -> None:
        if len(record.name) > MAX_LENGTH:
            record.name = f"...{record.name[-(MAX_LENGTH - 3) :]}"
