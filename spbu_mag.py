# encoding=utf-8

from common_html import makeSoup
from common_json import DEFAULT_SAVE_METHODS
from common_logging import logInfo, logWarning

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


def main(contests=None, saveMethods=DEFAULT_SAVE_METHODS):
    logInfo("----- СПбГУ (Магистратура) -----")

    if len(saveMethods) == 0:
        logWarning("Пустой список методов сохранения.")

    if contests is None:
        logInfo("Поиск конкурсов.")
        contests = findContests(SPBU_SITE)  # { contestId }
        logInfo("Найдено конкурсов: %d." % len(contests))

    contestLinks = addPrefixLinkToContests(contests)

    linkToAbits = findContestListsAsync(contestLinks)  # contestPage: { abit }

    logInfo("Обработано конкурсов: %d." % len(linkToAbits))
    logInfo("Найдено записей: %d. Готово." % sum(map(len, linkToAbits.values())))

    for saveMethod in saveMethods:
        saveMethod(linkToAbits, "spbu-mag")
    logInfo("Сохранено.")
