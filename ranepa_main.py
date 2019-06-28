# encoding=utf-8

import traceback
from typing import Tuple, Dict

from common_html import makeSoup, visibleSoupToString
from common_logging import logError, printDot
from common_task_queue import taskQueue

RANEPA_ROOT = "https://lk.ranepa.ru/pk/list.php"


# link - сайт с филиалами
def findDepartmentToLink(link: str) -> Tuple[Dict[str, str], int]:
    departments = dict()  # {department: link}

    for table in makeSoup(link).find_all("table"):
        if table.has_attr("class") and "ranepa-table" in table["class"]:
            for tbody in table.find_all("tbody"):
                for a in tbody.find_all("a"):
                    if a.has_attr("href"):
                        department = visibleSoupToString(a)
                        departments[department] = RANEPA_ROOT + a["href"]

                        printDot()

    return departments, len(departments)


# departments - {department: link}
def findDepartmentToSpecialityToLink(departments: Dict[str, str]) -> Tuple[Dict[str, Dict[str, str]], int]:
    specialities = dict()  # {department: {speciality: link}}
    specialityCount = [0]

    def addSpeciality(department, link):
        try:
            for table in makeSoup(link).find_all("table"):
                if table.has_attr("class") and "ranepa-table" in table["class"]:
                    for tbody in table.find_all("tbody"):
                        for a in tbody.find_all("a"):
                            if a.has_attr("href"):
                                speciality = visibleSoupToString(a)
                                specialities[department][speciality] = RANEPA_ROOT + a["href"]

                                specialityCount[0] += 1
                                printDot()
        except BaseException:
            logError("Ошибка в департаменте %s: %s" % (link, traceback.format_exc()))

    for department, link in departments.items():
        specialities[department] = dict()

        taskQueue.put((addSpeciality, (department, link)))

    taskQueue.join()

    return specialities, specialityCount[0]


# specialities - {department: {speciality: link}}
def findDepartmentToSpecialityToFormToLink(specialities: Dict[str, Dict[str, str]]) -> \
        Tuple[Dict[str, Dict[str, Dict[str, str]]], int]:
    forms = dict()  # {department: {speciality: {form: link}}}
    formCount = [0]

    def addForm(department, speciality, link):
        try:
            for table in makeSoup(link).find_all("table"):
                if table.has_attr("class") and "ranepa-table" in table["class"]:
                    for tbody in table.find_all("tbody"):
                        for a in tbody.find_all("a"):
                            if a.has_attr("href"):
                                form = visibleSoupToString(a)
                                forms[department][speciality][form] = RANEPA_ROOT + a["href"]

                                formCount[0] += 1
                                printDot()
        except BaseException:
            logError("Ошибка в форме %s: %s" % (link, traceback.format_exc()))

    for department, specialityDict in specialities.items():
        forms[department] = dict()

        for speciality, link in specialityDict.items():
            forms[department][speciality] = dict()

            taskQueue.put((addForm, (department, speciality, link)))

    taskQueue.join()

    return forms, formCount[0]


# forms - {department: {speciality: {form: link}}}
def findDepartmentToSpecialityToFormToEducationalProgramToLink(forms: Dict[str, Dict[str, Dict[str, str]]]) -> \
        Tuple[Dict[str, Dict[str, Dict[str, Dict[str, str]]]], int]:
    educationalPrograms = dict()  # {department: {speciality: {form: {educationalProgram: link}}}}
    educationalProgramCount = [0]

    def addEducationalProgram(department, speciality, form, link):
        try:
            for table in makeSoup(link).find_all("table"):
                if table.has_attr("class") and "ranepa-table" in table["class"]:
                    for tbody in table.find_all("tbody"):
                        for a in tbody.find_all("a"):
                            if a.has_attr("href"):
                                educationalProgram = visibleSoupToString(a)
                                educationalPrograms[department][speciality][form][educationalProgram] = RANEPA_ROOT + a["href"]

                                educationalProgramCount[0] += 1
                                printDot()
        except BaseException:
            logError("Ошибка в образовательной программе %s: %s" % (link, traceback.format_exc()))

    for department, specialityDict in forms.items():
        educationalPrograms[department] = dict()

        for speciality, formDict in specialityDict.items():
            educationalPrograms[department][speciality] = dict()

            for form, link in formDict.items():
                educationalPrograms[department][speciality][form] = dict()

                taskQueue.put((addEducationalProgram, (department, speciality, form, link)))

    taskQueue.join()

    return educationalPrograms, educationalProgramCount[0]
