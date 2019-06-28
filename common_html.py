# encoding=utf-8

import ssl
from time import sleep
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from common_logging import logWarning


def getSiteText(url: str, title: Optional[str] = None, time: int = 1, maxTimes: int = 3) -> Optional[str]:
    if time > maxTimes:
        message = "Не смог получить доступ к странице %s уже много раз (%d). Больше не буду пытаться."
        if title is None:
            message %= (url, maxTimes)
        else:
            message %= ("%s (%s)" % (url, title), maxTimes)
        logWarning(message)
        return None

    try:
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
        req = Request(url, headers={"User-Agent": userAgent})
        html = urlopen(req, context=ssl.SSLContext(ssl.PROTOCOL_SSLv23)).read().decode("utf-8")
        return html
    except (HTTPError, URLError) as e:
        message = "При попытке открыть %s произошла ошибка %s. Жду и пробую дальше! Осталось попыток: %d."
        remainingTimes = maxTimes - time
        if title is None:
            message %= (url, e, remainingTimes)
        else:
            message %= ("%s (%s)" % (url, title), e, remainingTimes)
        logWarning(message)
        if remainingTimes >= 1:
            sleep(1)
        return getSiteText(url, title=title, time=time + 1, maxTimes=maxTimes)


# Делает суп по ссылке.
# Если не удается сделать за maxTimes раз, сообщает о неудаче и отдает None
def makeSoup(url: str, title: str = None, maxTimes: int = 3) -> Optional[BeautifulSoup]:
    html = getSiteText(url, title=title, maxTimes=maxTimes)
    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")
    return soup


def soupToRawString(soup: BeautifulSoup) -> str:
    return soup.decode_contents().strip()


def visibleSoupToString(soup: BeautifulSoup) -> str:
    return (soup.find(text=True) or "").strip()
