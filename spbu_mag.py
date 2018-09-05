# encoding=utf-8
from common import makeSoup, visibleSoupToString, writeJson
from common_logging import logInfo, logWarning
from common_task_queue import taskQueue

from spbu_main import findContestListsAsync

SPBU_SITE = "https://cabinet.spbu.ru/Lists/Mag_EntryLists/"


# Поиск всех конкурсов
def findContests(spbuSite):
    contests = set()

    for a in makeSoup(spbuSite).find_all("a"):
        if a.has_attr("href"):
            contests.add(a["href"])

    contests.remove("#")

    return contests


def addPrefixLinkToContests(contests):
    return set(map(lambda contest: SPBU_SITE + contest, contests))


def main(contests=None):
    logInfo("----- СПбГУ (Магистратура) -----")

    if contests is None:
        logInfo("Поиск конкурсов.")
        contests = findContests(SPBU_SITE)  # { contestId }
        logInfo("Найдено конкурсов: %d." % len(contests))

    contestLinks = addPrefixLinkToContests(contests)

    contestLists = findContestListsAsync(contestLinks)  # contestPage: { abit }

    logInfo("Обработано конкурсов: %d." % len(contestLists))
    logInfo("Найдено записей: %d." % sum(map(len, contestLists.values())))

    for link, abits in contestLists.items():
        writeJson({"link": link, "abits": abits}, "spbu-mag/", link + ".json")
