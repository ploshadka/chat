import logging
import os
import time

# Папка для логов
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


# Форматтер с UTC-временем
class UTCFormatter(logging.Formatter):
    converter = time.gmtime

    def formatTime(self, record, datefmt=None):
        return super().formatTime(record, datefmt)


formatter = UTCFormatter(
    fmt='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Обработчики
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Логгер
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.propagate = False

# Добавляем обработчики
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
