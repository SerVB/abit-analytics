# encoding=utf-8

import logging
import sys

LOGGING_FORMAT = "%(asctime)s ::: %(levelname)s ::: %(message)s"
LOGGING_FILE = "lastLog.txt"
logging.basicConfig(handlers=[logging.FileHandler(LOGGING_FILE, "w", "utf-8")],
                    format=LOGGING_FORMAT,
                    level=logging.INFO)

_dotWasLogged = False  # Нужно ли переносить строку в консоли


def _ensureDotWasntLogged():
    global _dotWasLogged

    if _dotWasLogged:
        print()
        _dotWasLogged = False


# Логирует ошибку в консоль и в файл
def logError(message):
    _ensureDotWasntLogged()

    print("!Ошибка!", message)
    logging.error(message)


# Логирует предупреждение в консоль и в файл
def logWarning(message):
    _ensureDotWasntLogged()

    print("!Предупреждение!", message)
    logging.warning(message)


# Логирует сообщение в консоль и в файл
def logInfo(message):
    _ensureDotWasntLogged()

    print(message)
    logging.info(message)


# Ставит точку в консоль
def printDot():
    global _dotWasLogged

    print(".", end="")
    sys.stdout.flush()
    _dotWasLogged = True
