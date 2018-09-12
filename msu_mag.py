# encoding=utf-8

from common import getSiteText, makeSoup, soupToRawString, visibleSoupToString, PROPERTY, writeJsonPerPage, writeJsonPerUniversity
from common_logging import printDot, logInfo
from common_task_queue import taskQueue
from bs4 import BeautifulSoup


MSU_SITE = "http://cpk.msu.ru/"
DEPARTMENT_NAME_IDX = 1
ABIT_NAME_COL_IDX = 1


def findContestLinks():
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


def getContestsOnPage(siteText):
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


def getAbitsFromContest(contestOnPage, commonData):
    abits = list()
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


def findAbits(abits, contestLink):
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


def findAbitsAsync(contestLinks):
    abits = dict()

    for contestLink in contestLinks:
        taskQueue.put((findAbits, (abits, contestLink)))

    taskQueue.join()

    return abits


def main():
    logInfo("----- МГУ (Магистратура) -----")
    contestLinks = findContestLinks()
    linkToAbits = findAbitsAsync(contestLinks)

    writeJsonPerUniversity(linkToAbits, "msu-mag")
    # writeJsonPerPage(linkToAbits, "msu-mag")
