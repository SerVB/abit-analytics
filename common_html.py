# encoding=utf-8

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from time import sleep
import ssl

from common_logging import logWarning


def getSiteText(url, title=None, time=1, maxTimes=3):
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
def makeSoup(url, title=None, maxTimes=3):
    html = getSiteText(url, title=title, maxTimes=maxTimes)
    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")
    return soup


def soupToRawString(soup):
    return soup.decode_contents().strip()


def visibleSoupToString(soup):
    return (soup.find(text=True) or "").strip()
