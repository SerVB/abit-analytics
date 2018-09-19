# encoding=utf-8

from common_html import makeSoup, visibleSoupToString
from common_json import writeJsonPerUniversity, writeJsonPerPage
from common_logging import logInfo, logWarning
from common_task_queue import taskQueue

from spbu_main import findContestListsAsync

SPBU_SITE = "https://cabinet.spbu.ru/Lists/1k_EntryLists/"

NAME_COL_IDX = 2
CONTESTS_COL_IDX = 4

CONTESTS_SITE = "https://cabinet.spbu.ru/Lists/1k_EntryLists/data/%s.txt"


# Поиск всех ID всех абитуриентов:
# Поиск строк с тегами вида <td id="f585917a-d7af-499d-8299-e83624aeb8b7" ...>
def findAbitIds(spbuSite):
    abitIds = set()  # { (abitName, abitId) }

    for tr in makeSoup(spbuSite).find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < max(NAME_COL_IDX, CONTESTS_COL_IDX) or not tds[CONTESTS_COL_IDX].has_attr("id"):
            logWarning("Неправильная строка:" + str(tds))
            continue
        abitName = visibleSoupToString(tds[NAME_COL_IDX])
        abitId = tds[CONTESTS_COL_IDX]["id"]
        abitIds.add((abitName, abitId))

    return abitIds


def checkAbitCount(spbuSite, abitIds):
    abitCount = len(abitIds)
    logInfo("Найдено абитуриентов: %d." % abitCount)

    rowCount = len(makeSoup(spbuSite).find_all("tr"))
    if abitCount != rowCount - 1:
        message = "Подозрительно: незаголовочных строчек в таблице %d, а абитуриентов найдено %d."
        message %= (rowCount - 1, abitCount)
        logWarning(message)

# Добавляет конкурсы абитуриента в словарь abitContests
def extractContests(abitContests, abitName, abitId):
    abitContests[abitId] = set()
    soup = makeSoup(CONTESTS_SITE % abitId, title=abitName)
    if soup is None:
        return
    for a in soup.find_all("a"):
        if a.has_attr("href"):
            contestPage = a["href"]
            abitContests[abitId].add(contestPage[:contestPage.find("#")])


# Поиск всех конкурсов:
# Для каждого студента находим ссылки вида
# "list_fe7557c2-2287-4559-8006-238597740d08.html#b30a2f1e-b2be-4c7a-9951-71848bad5274"
# и отбрасываем якорную часть
def findAbitContestsAsync(abitIds):
    abitContests = dict()  # abitId: { contestId }

    for abitName, abitId in abitIds:
        taskQueue.put((extractContests, (abitContests, abitName, abitId)))

    taskQueue.join()

    return abitContests


def flattenAbitContests(abitContests):
    contests = set()

    for abitId, abitContest in abitContests.items():
        for contest in abitContest:
            contests.add(contest)

    return contests


def addPrefixLinkToContests(contests):
    return set(map(lambda contest: SPBU_SITE + contest, contests))


def flattenContestLists(contestLists):
    lists = []

    for contestPage, contestRows in contestLists.items():
        for row in contestRows:
            lists.append(row)

    return lists


def main(contests=None):
    logInfo("----- СПбГУ (Бакалавриат) -----")

    if contests is None:
        logInfo("Поиск всех конкурсов. Чтобы получить полный список, нужно сделать около десяти тысяч запросов, поэтому это займет долгое время...")

        abitIds = findAbitIds(SPBU_SITE)  # { (abitName, abitId) }
        checkAbitCount(SPBU_SITE, abitIds)

        abitContests = findAbitContestsAsync(abitIds)  # abitId: { contestId }

        contests = flattenAbitContests(abitContests)  # { contestId }

        logInfo("Найдено конкурсов: %d." % len(contests))

    contestLinks = addPrefixLinkToContests(contests)

    linkToAbits = findContestListsAsync(contestLinks)  # contestPage: { abit }

    logInfo("Обработано конкурсов: %d." % len(linkToAbits))
    logInfo("Найдено записей: %d." % sum(map(len, linkToAbits.values())))

    writeJsonPerUniversity(linkToAbits, "spbu-bach")
    # writeJsonPerPage(linkToAbits, "spbu-bach")
