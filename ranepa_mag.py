# encoding=utf-8
import traceback

from common_logging import logInfo, logWarning, logError, printDot

from common import writeJson, PROPERTY, makeSoup, visibleSoupToString, soupToRawString

from common_task_queue import taskQueue

from ranepa_main import findDepartmentToLink
from ranepa_main import findDepartmentToSpecialityToLink
from ranepa_main import findDepartmentToSpecialityToFormToLink
from ranepa_main import findDepartmentToSpecialityToFormToEducationalProgramToLink


RANEPA_SITE = "https://lk.ranepa.ru/pk/list.php?FT=1&FL=1"


# educationalPrograms - # {department: {speciality: {form: {educationalProgram: link}}}}
def findLinkToAbit(educationalPrograms):
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

                    assert -42 not in (fioIdx, statusIdx, sumIdx, individualBonusIdx)

                    subjectsBeginIdx = sumIdx + 1
                    subjects = list(map(
                        visibleSoupToString,
                        section.find("thead").find_all("th")[subjectsBeginIdx:individualBonusIdx]
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
                            abit[PROPERTY.SUM] = float(visibleSoupToString(tds[sumIdx]))
                        except ValueError:
                            abit[PROPERTY.SUM] = None
                        for idx, subj in enumerate(subjects):
                            try:
                                abit[PROPERTY.GRADES][subj] = float(visibleSoupToString(tds[subjectsBeginIdx + idx]))
                            except ValueError:
                                abit[PROPERTY.GRADES][subj] = None
                        abit[PROPERTY.EXTRA_BONUS] = float(visibleSoupToString(tds[individualBonusIdx]))
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
def main(department=None):
    logInfo("----- РАНХиГС (Магистратура) -----")
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

    linkToAbit, count = findLinkToAbit(departmentToSpecialityToFormToEducationalProgramToLink)
    logInfo("Всего абитуриентов найдено: %s." % count)

    for link, abits in linkToAbit.items():
        writeJson({"link": link, "abits": abits}, "ranepa-mag/", link + ".json")

    logInfo("Json файлов записано: %s. Завершено." % len(linkToAbit))
