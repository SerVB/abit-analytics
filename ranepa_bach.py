# encoding=utf-8

import traceback
from typing import Dict, Tuple, Optional

from common_html import makeSoup, visibleSoupToString, soupToRawString
from common_json import DEFAULT_SAVE_METHODS
from common_logging import logInfo, logWarning, logError, printDot
from common_properties import PROPERTY
from common_task_queue import taskQueue
from ranepa_main import findDepartmentToLink
from ranepa_main import findDepartmentToSpecialityToFormToEducationalProgramToLink
from ranepa_main import findDepartmentToSpecialityToFormToLink
from ranepa_main import findDepartmentToSpecialityToLink

RANEPA_SITE = "https://lk.ranepa.ru/pk/list.php?FT=1&FL=0"


# educationalPrograms - # {department: {speciality: {form: {educationalProgram: link}}}}
def findLinkToAbit(educationalPrograms: Dict[str, Dict[str, Dict[str, Dict[str, str]]]]) -> \
        Tuple[Dict[str, list], int]:
    links = dict()  # {link: [abits]}
    abitCount = [0]

    def addAbits(department, speciality, form, educationalProgram, link):
        try:
            abits = list()
            for section in makeSoup(link).find_all("section"):
                def sectionIsEmpty(section):
                    return 'style="text-align:center">Список пуст</td>' in soupToRawString(section)

                if sectionIsEmpty(section):
                    continue

                if section.has_attr("id") and section["id"] in ("list_budget", "list_contract"):
                    fioIdx = -42
                    statusIdx = -42
                    sumIdx = -42
                    individualBonusIdx = -42
                    extraRightIdx = -42  # предметы находятся в [individualBonusIdx + 1, extraRightIdx)
                    originalIdx = -1

                    for idx, td in enumerate(section.find("thead").find_all("th")):
                        contents = visibleSoupToString(td)
                        if "ФИО" in contents:
                            fioIdx = idx
                        elif "Статус" in contents:
                            statusIdx = idx
                        elif "Сумма конкурсных баллов" in contents:
                            sumIdx = idx
                        elif "Сумма баллов по индивидуальным достижениям" in contents:
                            individualBonusIdx = idx
                        elif "Преимущественное право" in contents:
                            extraRightIdx = idx

                    assert -42 not in (fioIdx, statusIdx, sumIdx, individualBonusIdx, extraRightIdx)

                    subjectsBeginIdx = individualBonusIdx + 1
                    subjects = list(map(
                        visibleSoupToString,
                        section.find("thead").find_all("th")[subjectsBeginIdx:extraRightIdx]
                    ))

                    for tr in section.find("tbody").find_all("tr"):
                        abit = dict()

                        abit[PROPERTY.DEPARTMENT] = department
                        abit[PROPERTY.SPECIALITY] = speciality
                        abit[PROPERTY.EDU_PROG] = educationalProgram
                        abit[PROPERTY.ONLY_IN_WALLS] = form
                        abit[PROPERTY.FOR_MONEY] = section["id"] == "list_contract"

                        tds = tr.find_all("td")

                        abit[PROPERTY.ABIT_NAME] = visibleSoupToString(tds[fioIdx])
                        abit[PROPERTY.CONTEST_TYPE] = visibleSoupToString(tds[statusIdx])
                        abit[PROPERTY.GRADES] = dict()
                        try:
                            abit[PROPERTY.SUM] = int(visibleSoupToString(tds[sumIdx]))
                        except ValueError:
                            abit[PROPERTY.SUM] = None
                        for idx, subj in enumerate(subjects):
                            try:
                                abit[PROPERTY.GRADES][subj] = int(visibleSoupToString(tds[subjectsBeginIdx + idx]))
                            except ValueError:
                                abit[PROPERTY.GRADES][subj] = None
                        abit[PROPERTY.EXTRA_BONUS] = int(visibleSoupToString(tds[individualBonusIdx]))
                        abit[PROPERTY.ORIGINAL] = visibleSoupToString(tds[originalIdx]) == "Оригинал"

                        abits.append(abit)

            abitCount[0] += len(abits)
            links[link] = abits
            printDot()
        except BaseException:
            logError("Ошибка в списке %s: %s" % (link, traceback.format_exc()))

    for department, specialityDict in educationalPrograms.items():
        for speciality, formDict in specialityDict.items():
            for form, educationalProgramDict in formDict.items():
                for educationalProgram, link in educationalProgramDict.items():
                    taskQueue.put((addAbits, (department, speciality, form, educationalProgram, link)))

    taskQueue.join()

    return links, abitCount[0]


# Филиал - строка. Для всех доступных филиалов None
def main(department: Optional[str] = None, saveMethods=DEFAULT_SAVE_METHODS):
    logInfo("----- РАНХиГС (Бакалавриат) -----")

    if len(saveMethods) == 0:
        logWarning("Пустой список методов сохранения.")

    logInfo("Начат поиск филиалов.")

    departmentToLink, count = findDepartmentToLink(RANEPA_SITE)
    if department is not None:
        departmentToLink = {department: departmentToLink[department]}
        count = 1
    logInfo("Филиалов найдено: %s. Начат поиск направлений." % count)

    departmentToSpecialityToLink, count = findDepartmentToSpecialityToLink(departmentToLink)
    logInfo("Направлений найдено: %s. Начат поиск форм." % count)

    departmentToSpecialityToFormToLink, count = findDepartmentToSpecialityToFormToLink(departmentToSpecialityToLink)
    logInfo("Форм найдено: %s. Начат поиск образовательных программ." % count)

    departmentToSpecialityToFormToEducationalProgramToLink, count = findDepartmentToSpecialityToFormToEducationalProgramToLink(departmentToSpecialityToFormToLink)
    logInfo("Образовательных программ найдено: %s. Начат поиск абитуриентов." % count)

    linkToAbits, count = findLinkToAbit(departmentToSpecialityToFormToEducationalProgramToLink)
    logInfo("Найдено записей: %s. Готово." % count)

    for saveMethod in saveMethods:
        saveMethod(linkToAbits, "ranepa-bach")
    logInfo("Сохранено.")
