# encoding=utf-8

import json
from common import writeJson, getSiteText, PROPERTY
from common_logging import logInfo, printDot
from common_task_queue import taskQueue


RGGU_SITE_BUDGET = "http://apply.rggu.ru/magistratura_list_budget/"
RGGU_SITE_CONTRACT = "http://apply.rggu.ru/magistratura_list_contract/"


def findContestLinks(rgguSite):
    jsonLink = rgguSite + "json/%s.json"

    mainJsonLink = jsonLink % ".config"
    mainJsonContent = json.loads(getSiteText(mainJsonLink))

    contestLinks = list(map(lambda item: jsonLink % item["file"], mainJsonContent["list"]))
    return contestLinks


def findAbits(abits, contestSite, additionalParameters):
    jsonContent = json.loads(getSiteText(contestSite))

    commonData = dict(additionalParameters)
    commonData[PROPERTY.ONLY_IN_WALLS] = jsonContent["meta"]["form_of_study"]
    commonData[PROPERTY.SPECIALITY] = jsonContent["meta"]["field_of_study"]

    answer = list()  # [abits]

    for abitData in jsonContent["list"]:
        abit = dict(commonData)

        for i, cell in enumerate(abitData):
            abit[jsonContent["header"][i]] = cell

        answer.append(abit)

    abits[contestSite] = answer
    printDot()


def findAbitsAsync(contestLinks, additionalParameters):
    abits = dict()  # {link: [abits]}

    for contestLink in contestLinks:
        taskQueue.put((findAbits, (abits, contestLink, additionalParameters)))

    taskQueue.join()

    return abits


def parseSite(link, additionalParameters):
    contestLinks = findContestLinks(link)
    logInfo("Конкурсов найдено: %s." % len(contestLinks))

    linkToAbit = findAbitsAsync(contestLinks, additionalParameters)
    for link, abits in linkToAbit.items():
        writeJson({"link": link, "abits": abits}, "rggu-mag/", link)


def main():
    logInfo("----- РГГУ (Магистратура) -----")

    parseSite(RGGU_SITE_BUDGET, {PROPERTY.FOR_MONEY: False})
    parseSite(RGGU_SITE_CONTRACT, {PROPERTY.FOR_MONEY: True})
