from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import logging

LOGGING_FORMAT = "%(asctime)s:::%(levelname)s:::%(message)s"
LOGGING_FILE = "lastLog.txt"
logging.basicConfig(handlers=[logging.FileHandler(LOGGING_FILE, "w", "utf-8")],
                    format=LOGGING_FORMAT,
                    level=logging.INFO)


# Логирует ошибку в консоль и в файл
def logError(message):
    print("!Ошибка!", message)
    logging.error(message)


# Логирует предупреждение в консоль и в файл
def logWarning(message):
    print("!Предупреждение!", message)
    logging.warning(message)


# Логирует сообщение в консоль и в файл
def logInfo(message):
    print(message)
    logging.info(message)


# Делает пустой суп
def makeDummySoup():
    return BeautifulSoup("dummy html", "html.parser")


# Делает суп по ссылке.
# Если не удается сделать за maxTimes раз, сообщает о неудаче и отдает пустой суп
def makeSoup(url, title=None, time=1, maxTimes=5):
    if time > maxTimes:
        message = "Не смог получить доступ к странице %s уже %d раз. Больше не буду пытаться."
        if title is None:
            message %= (url, maxTimes)
        else:
            message %= ("%s (%s)" % (url, title), maxTimes)
        logWarning(message)
        return makeDummySoup()

    try:
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
        req = Request(url, headers={"User-Agent": userAgent})  # На всякий случай пробуем маскироваться
        html = urlopen(req).read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except (HTTPError, URLError) as e:
        message = "При попытке открыть %s произошла ошибка %s. Жду и пробую дальше! " \
                  "Осталось попыток: %d."
        remainingTimes = maxTimes - time
        if title is None:
            message %= (url, e, remainingTimes)
        else:
            message %= ("%s (%s)" % (url, title), e, remainingTimes)
        logWarning(message)
        if remainingTimes >= 1:
            sleep(1)
        return makeSoup(url, title=title, time=time + 1, maxTimes=maxTimes)


logInfo("----- СПбГУ -----")
SPBU_SITE = "https://cabinet.spbu.ru/Lists/1k_EntryLists/"
NAME_COL = 2
CONTESTS_COL = 4

soup = makeSoup(SPBU_SITE)

# Поиск всех ID всех абитуриентов:
# Поиск строк с тегами вида <td id="f585917a-d7af-499d-8299-e83624aeb8b7" ...>
abitIds = set()  # { (abitName, abitId) }
for tr in soup.find_all("tr"):
    tds = tr.find_all("td")
    if len(tds) < max(NAME_COL, CONTESTS_COL) or not tds[CONTESTS_COL].has_attr("id"):
        continue
    abitName = tds[NAME_COL].decode_contents()
    abitId = tds[CONTESTS_COL]["id"]
    abitIds.add((abitName, abitId))

abitCount = len(abitIds)
logInfo("Найдено абитуриентов: %d." % abitCount)

rowCount = len(soup.find_all("tr"))
if abitCount != rowCount - 1:
    message = "Подозрительно: незаголовочных строчек в таблице %d, а абитуриентов найдено %d."
    message %= (rowCount - 1, abitCount)
    logWarning(message)

# Поиск всех конкурсов:
# Для каждого студента находим ссылки вида
# "list_fe7557c2-2287-4559-8006-238597740d08.html#b30a2f1e-b2be-4c7a-9951-71848bad5274"
# и отбрасываем якорную часть
abitContests = dict()  # abitId: { contestId }
CONTESTS_SITE = "https://cabinet.spbu.ru/Lists/1k_EntryLists/data/%s.txt"


# Добавляет конкурсы абитуриента в словарь abitContests
def extractContests(abitName, abitId):
    abitContests[abitId] = set()
    soup = makeSoup(CONTESTS_SITE % abitId, title=abitName)
    for a in soup.find_all("a"):
        if a.has_attr("href"):
            contestPage = a["href"]
            abitContests[abitId].add(contestPage[:contestPage.find("#")])


abitTasks = set()
for abitName, abitId in abitIds:
    task = Thread(target=extractContests, args=(abitName, abitId))
    abitTasks.add(task)
    task.start()

for task in abitTasks:
    task.join()

contests = set()

for abitId, abitContest in abitContests.items():
    for contest in abitContest:
        contests.add(contest)

contestCount = len(contests)
logInfo("Найдено конкурсов: %d." % contestCount)
