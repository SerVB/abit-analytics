# encoding=utf-8

from typing import List, Dict

from bs4 import BeautifulSoup

from common_html import getSiteText, makeSoup, soupToRawString, visibleSoupToString
from common_json import DEFAULT_SAVE_METHODS
from common_logging import printDot, logInfo, logWarning
from common_properties import PROPERTY
from common_task_queue import taskQueue

MSU_SITE = "http://cpk.msu.ru/"
DEPARTMENT_NAME_IDX = 1
ABIT_NAME_COL_IDX = 1


def findContestLinks() -> List[str]:
    siteText = getSiteText(MSU_SITE + "daily").replace('"', "'")
    beginMagIdx = siteText.find("<br", siteText.find("id='sections_m'"))
    endMagIdx = siteText.find("<br", siteText.find("id='sections_2v'"))
    magList = siteText[beginMagIdx:endMagIdx]

    magListSoup = BeautifulSoup(magList, "html.parser")

    contests = list()

    for li in magListSoup.find("ul").find_all("li"):
        a = li.find("a")
        if a.has_attr("href"):
            contests.append(MSU_SITE + a["href"])

    return contests


def getContestsOnPage(siteText: str) -> List[str]:
    answer = list()
    h4 = siteText.find("<h4 id")
    endFound = False
    while not endFound:
        nextH4 = siteText.find("<h4 id", h4 + 1)
        if nextH4 == -1:
            nextH4 = siteText.find("</div", h4)
            endFound = True
        answer.append(siteText[h4:nextH4])
        h4 = nextH4
    return answer


def getAbitsFromContest(contestOnPage: str, commonData: Dict[str, str]) -> List[Dict[str, str]]:
    abits: List[Dict[str, str]] = list()
    contestOnPageSoup = BeautifulSoup(contestOnPage, "html.parser")
    contestCommonData = dict(commonData)
    contestCommonData[PROPERTY.SPECIALITY] = visibleSoupToString(contestOnPageSoup.find("h4"))
    contestCommonData[PROPERTY.ONLY_IN_WALLS] = tuple(filter(lambda s: "форма обучения" in s, map(visibleSoupToString, contestOnPageSoup.find_all("b"))))[0]

    for tr in contestOnPageSoup.find_all("tr"):
        abitName = visibleSoupToString(tr.find_all("td")[ABIT_NAME_COL_IDX])
        abitData = dict(contestCommonData)
        abitData[PROPERTY.ABIT_NAME] = abitName

        abits.append(abitData)

    return abits


def findAbits(abits: Dict[str, list], contestLink: str) -> None:
    soup = makeSoup(contestLink)

    commonData = dict()
    commonData[PROPERTY.DEPARTMENT] = visibleSoupToString(soup.find_all("h3")[DEPARTMENT_NAME_IDX])

    siteText = soupToRawString(soup)

    contestsOnPage = getContestsOnPage(siteText)

    answer = list()

    for contestOnPage in contestsOnPage:
        answer += getAbitsFromContest(contestOnPage, commonData)

    abits[contestLink] = answer
    printDot()


def findAbitsAsync(contestLinks: List[str]) -> Dict[str, List]:
    abits: Dict[str, List[str, str]] = dict()

    for contestLink in contestLinks:
        taskQueue.put((findAbits, (abits, contestLink)))

    taskQueue.join()

    return abits


def main(saveMethods=DEFAULT_SAVE_METHODS) -> None:
    logInfo("----- МГУ (Магистратура) -----")

    if len(saveMethods) == 0:
        logWarning("Пустой список методов сохранения.")

    logInfo("Начат поиск конкурсов.")
    contestLinks = findContestLinks()
    logInfo("Конкурсов найдено: %d. Начат поиск поступающих." % len(contestLinks))
    linkToAbits = findAbitsAsync(contestLinks)
    logInfo("Найдено записей: %d. Готово." % sum(map(len, linkToAbits.values())))

    for saveMethod in saveMethods:
        saveMethod(linkToAbits, "msu-mag")
    logInfo("Сохранено.")


if __name__ == "__main__":
    main()
