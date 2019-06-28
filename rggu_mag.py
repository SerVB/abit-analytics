# encoding=utf-8

import json
from typing import List

from common_html import getSiteText
from common_json import DEFAULT_SAVE_METHODS
from common_logging import logInfo, logWarning, printDot
from common_properties import PROPERTY
from common_task_queue import taskQueue

RGGU_SITE_BUDGET = "http://apply.rggu.ru/magistratura_list_budget/"
RGGU_SITE_CONTRACT = "http://apply.rggu.ru/magistratura_list_contract/"


def findContestLinks(rgguSite: str) -> List[str]:
    jsonLink = rgguSite + "json/%s.json"

    mainJsonLink = jsonLink % ".config"
    mainJsonContent = json.loads(getSiteText(mainJsonLink))

    contestLinks = list(map(lambda item: jsonLink % item["file"], mainJsonContent["list"]))
    return contestLinks


def findAbits(abits: dict, contestSite: str, additionalParameters: dict) -> None:
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


def findAbitsAsync(contestLinks: List[str], additionalParameters: dict) -> dict:
    abits = dict()  # {link: [abits]}

    for contestLink in contestLinks:
        taskQueue.put((findAbits, (abits, contestLink, additionalParameters)))

    taskQueue.join()

    return abits


def parseSite(link: str, additionalParameters: dict) -> dict:
    contestLinks = findContestLinks(link)
    logInfo("Конкурсов найдено: %s." % len(contestLinks))

    return findAbitsAsync(contestLinks, additionalParameters)


def main(saveMethods=DEFAULT_SAVE_METHODS) -> None:
    logInfo("----- РГГУ (Магистратура) -----")

    if len(saveMethods) == 0:
        logWarning("Пустой список методов сохранения.")

    logInfo("Начат поиск бюджетников.")
    linkToAbitsBudget = parseSite(RGGU_SITE_BUDGET, {PROPERTY.FOR_MONEY: False})
    logInfo("Бюджетных конкурсов найдено: %d. Начат поиск контрактников." % len(linkToAbitsBudget))
    linkToAbitsContract = parseSite(RGGU_SITE_CONTRACT, {PROPERTY.FOR_MONEY: True})
    logInfo("Контрактных конкурсов найдено: %d. Начато слитие конкурсов." % len(linkToAbitsContract))

    linkToAbits = {**linkToAbitsBudget, **linkToAbitsContract}

    logInfo("Найдено записей: %d. Готово." % sum(map(len, linkToAbits.values())))

    for saveMethod in saveMethods:
        saveMethod(linkToAbits, "rggu-mag")
    logInfo("Сохранено.")
