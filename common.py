# encoding=utf-8
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from time import sleep
import ssl
import json
import os
from common_logging import logInfo, logWarning
import urllib.parse


class PROPERTY:
    ABIT_NAME = "abitName"
    BIRTHDAY = "birthday"
    SPECIALITY = "speciality"
    EDU_PROG = "eduProg"
    FOR_MONEY = "forMoney"
    GRADES = "grades"
    SUM = "sum"
    SUM_EXAM = "sumExam"
    EXTRA_BONUS = "extraBonus"
    ORIGINAL = "original"
    ONLY_IN_WALLS = "onlyInWalls"
    CONTEST_TYPE = "contestType"
    DEPARTMENT = "department"


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
def makeSoup(url, title=None, time=1, maxTimes=3):
    html = getSiteText(url, title=title, maxTimes=maxTimes)
    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")
    return soup


def writeJson(jsonData, dirName, fileName):
    dirName = "output/" + dirName

    if not os.path.exists(dirName):
        os.makedirs(dirName)

    fileName = "output/" + dirName + urllib.parse.quote_plus(fileName).replace("\\", "/")

    suffixName = fileName[fileName.rfind("/") + 1:]
    if len(suffixName) > 255:  # Ограничение Windows
        suffixName = suffixName[-255:]

    fileName = dirName + suffixName

    with open(fileName, "w", encoding="utf-8") as outputFile:
        print(json.dumps(jsonData, ensure_ascii=False, indent=2), file=outputFile)
        logInfo("JSON файл '%s' записан." % fileName)


def soupToRawString(soup):
    return soup.decode_contents().strip()


def strOrEmpty(obj):
    if obj is None:
        return ""
    return str(obj)


def visibleSoupToString(soup):
    return strOrEmpty(soup.find(text=True)).strip()
