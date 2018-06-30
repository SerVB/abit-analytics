from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import logging
import json

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
def makeSoup(url, title=None, time=1, maxTimes=3):
    if time > maxTimes:
        message = "Не смог получить доступ к странице %s уже много раз (%d). Больше не буду пытаться."
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
NAME_COL_IDX = 2
CONTESTS_COL_IDX = 4

soup = makeSoup(SPBU_SITE)

# Поиск всех ID всех абитуриентов:
# Поиск строк с тегами вида <td id="f585917a-d7af-499d-8299-e83624aeb8b7" ...>
abitIds = set()  # { (abitName, abitId) }
for tr in soup.find_all("tr")[1:]:
    tds = tr.find_all("td")
    if len(tds) < max(NAME_COL_IDX, CONTESTS_COL_IDX) or not tds[CONTESTS_COL_IDX].has_attr("id"):
        logWarning("Неправильная строка:" + str(tds))
        continue
    abitName = tds[NAME_COL_IDX].decode_contents().strip()
    abitId = tds[CONTESTS_COL_IDX]["id"]
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


class PROPERTY:
    ABIT_NAME = "abitName"
    BIRTHDAY = "birthday"
    SPECIALTY = "specialty"
    EDU_PROG = "eduProg"
    FOR_MONEY = "forMoney"
    GRADES = "grades"
    SUM = "sum"
    EXTRA_BONUS = "extraBonus"
    ORIGINAL = "original"
    ONLY_IN_WALLS = "onlyInWalls"
    CONTEST_TYPE = "contestType"


def getValue(str):
    return str[str.rfind(">") + 1:].strip()


contestLists = dict()  # contestPage: { abit }


def getSubjectCount(soup):
    return max(map(lambda s: int(s[0]), soup.decode_contents().split("ВИ ")[1:]))


def getFloatGrade(soup):
    try:  # TODO: (О) отбрасывается, правильно ли это?
        return float(soup.decode_contents().replace(",", ".").replace("(О)", "").strip())
    except:  # TODO: Заменить этот перехват любых исключений?
        return None


def extractList(contestPage):
    fullPath = SPBU_SITE + contestPage
    soup = makeSoup(fullPath)

    subjectCount = getSubjectCount(soup)

    properties = soup.find_all("p")[0].decode_contents().split("<br/>")
    listProperties = dict()

    subjects = dict()

    for property in properties:
        if "Образовательная программа:" in property:
            listProperties[PROPERTY.EDU_PROG] = getValue(property)
        elif "Направление:" in property:
            listProperties[PROPERTY.SPECIALTY] = getValue(property)
        elif "Форма обучения:" in property:
            form = getValue(property)
            if form == "очно-заочная":
                listProperties[PROPERTY.ONLY_IN_WALLS] = False
            elif form == "очная":
                listProperties[PROPERTY.ONLY_IN_WALLS] = True
            else:
                logWarning("Найдена неизвестная форма обучения: '" + form + "'. Не добавляю это свойство.")
        elif "Основа обучения:" in property:
            form = getValue(property)
            if form == "Договорная":
                listProperties[PROPERTY.FOR_MONEY] = True
            elif form == "Госбюджетная":
                listProperties[PROPERTY.FOR_MONEY] = False
            else:
                logWarning("Найдена неизвестная основа обучения: '" + form + "'. Не добавляю это свойство.")
        elif "ВИ " in property:
            number = int(property[property.find(":") - 1])
            subject = property[property.find(":") + 1:].replace("</b>", "").strip()
            subjects[number] = subject

    NAME_COL_IDX = 2
    BIRTHDAY_COL_IDX = NAME_COL_IDX + 1
    CONTEST_TYPE_COL_IDX = BIRTHDAY_COL_IDX + 1
    isContract = listProperties[PROPERTY.FOR_MONEY]
    SUM_COL_IDX = CONTEST_TYPE_COL_IDX + 1 + int(not isContract)  # Приоритет указывается только для бюджета
    FIRST_GRADE_COL_IDX = SUM_COL_IDX + 2
    EXTRA_BONUS_COL_IDX = FIRST_GRADE_COL_IDX + subjectCount
    ORIGINAL_COL_IDX = EXTRA_BONUS_COL_IDX + 1

    abits = []

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < ORIGINAL_COL_IDX + 1 or not tds[0].decode_contents().strip().isdigit():
            continue

        abit = dict(listProperties)
        name = tds[NAME_COL_IDX].decode_contents()
        abit[PROPERTY.ABIT_NAME] = name[name.rfind(">") + 1:].strip()
        abit[PROPERTY.BIRTHDAY] = tds[BIRTHDAY_COL_IDX].decode_contents().strip()
        contestType = tds[CONTEST_TYPE_COL_IDX].decode_contents().strip()
        if contestType in ("общ.", "дог.", "общ-преим", "дог-преим"):  # TODO: правильно ли все эти сохранять как одно?
            abit[PROPERTY.CONTEST_TYPE] = "common"
        elif contestType == "б/э":
            abit[PROPERTY.CONTEST_TYPE] = "bvi"
        elif contestType == "в/к":
            abit[PROPERTY.CONTEST_TYPE] = "vk"
        else:
            logWarning("Неизвестный тип конкурса '" + contestType + "' у абитуриента '" +
                       abit[PROPERTY.ABIT_NAME] + "' на '" + fullPath + "'. Не добавляю это свойство.")
        abit[PROPERTY.GRADES] = dict()
        abit[PROPERTY.GRADES][PROPERTY.SUM] = getFloatGrade(tds[SUM_COL_IDX])
        for i in range(subjectCount):
            abit[PROPERTY.GRADES][subjects[i + 1]] = getFloatGrade(tds[FIRST_GRADE_COL_IDX + i])
        abit[PROPERTY.EXTRA_BONUS] = getFloatGrade(tds[EXTRA_BONUS_COL_IDX])
        abit[PROPERTY.ORIGINAL] = tds[ORIGINAL_COL_IDX].decode_contents().strip() == "Да"
        abit["source-page"] = fullPath  # Для дебага

        abits.append(abit)

    contestLists[contestPage] = abits


contestTasks = set()
for contests in contests:
    task = Thread(target=extractList, args=(contests,))
    contestTasks.add(task)
    task.start()

for task in contestTasks:
    task.join()

logInfo("Обработано конкурсов: %d." % len(contestLists))
logInfo("Найдено записей: %d." % sum(map(len, contestLists.values())))

lists = []

for contestPage, contestRows in contestLists.items():
    for row in contestRows:
        lists.append(row)

with open("data.json", "w", encoding="utf-8") as f:
    print(json.dumps(lists, ensure_ascii=False, indent=2), file=f)  # TODO: параметры JSON норм?
    logInfo("JSON записан.")
