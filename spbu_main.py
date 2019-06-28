# encoding=utf-8

from common_html import makeSoup, soupToRawString, visibleSoupToString
from common_logging import printDot, logInfo, logWarning
from common_properties import PROPERTY
from common_task_queue import taskQueue


def getValue(line):
    return line[line.rfind(">") + 1:].strip()


def getFloatGrade(soup):
    try:  # TODO: (О) отбрасывается, правильно ли это?
        return float(visibleSoupToString(soup).replace(",", ".").replace("(О)", ""))
    except:  # TODO: Заменить этот перехват любых исключений?
        return None


def extractList(contestLists, contestPage):
    soup = makeSoup(contestPage)

    if soup is None:
        return

    listProperties = dict()
    subjects = list()

    properties = soupToRawString(soup).split("<br/>")
    for property in properties:
        if "table" in property:
            continue

        if "Образовательная программа:" in property:
            listProperties[PROPERTY.EDU_PROG] = getValue(property)
        elif "Направление:" in property:
            listProperties[PROPERTY.SPECIALITY] = getValue(property)
        elif "Форма обучения:" in property:
            listProperties[PROPERTY.ONLY_IN_WALLS] = getValue(property)
        elif "Основа обучения:" in property:
            listProperties[PROPERTY.FOR_MONEY] = getValue(property)
        elif "ВИ " in property:
            subject = property[property.rfind(":") + 1:].replace("</b>", "").strip()
            subjects.append(subject)

    NAME_COL_IDX = -42
    BIRTHDAY_COL_IDX = None  # У магистратуры нет
    CONTEST_TYPE_COL_IDX = -42
    SUM_COL_IDX = None  # У магистратуры нет
    SUM_EXAM_COL_IDX = None  # У магистратуры нет
    FIRST_GRADE_COL_IDX = None  # Может не быть вступительных испытаний. Например, если пустая страница
    EXTRA_BONUS_COL_IDX = -42
    ORIGINAL_COL_IDX = -42

    for i, th in enumerate(soup.find("tr").find_all("th")):
        text = visibleSoupToString(th)
        if "Фамилия Имя Отчество" in text or "ФИО" in text:
            NAME_COL_IDX = i
        elif "Дата рождения" in text:
            BIRTHDAY_COL_IDX = i
        elif "Тип конкурса" in text:
            CONTEST_TYPE_COL_IDX = i
        elif "Σ общ" in text:
            SUM_COL_IDX = i
        elif "Σ ЕГЭ" in text:
            SUM_EXAM_COL_IDX = i
        elif FIRST_GRADE_COL_IDX is None and "ВИ " in text:
            FIRST_GRADE_COL_IDX = i
        elif "Σ ИД" in text:
            EXTRA_BONUS_COL_IDX = i
        elif "Оригинал" in text:
            ORIGINAL_COL_IDX = i

    assert -42 not in (NAME_COL_IDX, CONTEST_TYPE_COL_IDX, EXTRA_BONUS_COL_IDX, ORIGINAL_COL_IDX)

    abits = []

    for tr in soup.find_all("tr")[1:]:
        tds = tr.find_all("td")

        abit = dict(listProperties)
        abit[PROPERTY.ABIT_NAME] = visibleSoupToString(tds[NAME_COL_IDX])
        if BIRTHDAY_COL_IDX is not None:
            abit[PROPERTY.BIRTHDAY] = visibleSoupToString(tds[BIRTHDAY_COL_IDX])
        abit[PROPERTY.CONTEST_TYPE] = visibleSoupToString(tds[CONTEST_TYPE_COL_IDX])
        if SUM_COL_IDX is not None:
            abit[PROPERTY.SUM] = getFloatGrade(tds[SUM_COL_IDX])
        if SUM_EXAM_COL_IDX is not None:
            abit[PROPERTY.SUM_EXAM] = getFloatGrade(tds[SUM_EXAM_COL_IDX])
        if FIRST_GRADE_COL_IDX is None:
            abit[PROPERTY.GRADES] = None
        else:
            abit[PROPERTY.GRADES] = dict()
            for i in range(len(subjects)):
                abit[PROPERTY.GRADES][subjects[i]] = getFloatGrade(tds[FIRST_GRADE_COL_IDX + i])
        abit[PROPERTY.EXTRA_BONUS] = getFloatGrade(tds[EXTRA_BONUS_COL_IDX])
        abit[PROPERTY.ORIGINAL] = visibleSoupToString(tds[ORIGINAL_COL_IDX]) == "Да"

        abits.append(abit)

    contestLists[contestPage] = abits
    printDot()


def findContestListsAsync(contestLinks):
    contestLists = dict()  # contestPage: { abit }

    for contestLink in contestLinks:
        taskQueue.put((extractList, (contestLists, contestLink)))

    taskQueue.join()

    return contestLists


# Поиск всех конкурсов
def findContests(spbuSite):
    contests = list()

    for a in makeSoup(spbuSite).find_all("a"):
        if a.has_attr("href"):
            contests.append(a["href"])

    del (contests[0])  # Удалить ссылку на предыдущую страницу

    return contests


def addPrefixLinkToContests(spbuSite, contests):
    siteDir = spbuSite[:spbuSite.rfind("/")] + "/"
    return set(map(lambda contest: siteDir + contest, contests))


def parseSpbu(contests, saveMethods, spbuSite, name, saveDir):
    logInfo("----- %s -----" % name)

    if len(saveMethods) == 0:
        logWarning("Пустой список методов сохранения.")

    if contests is None:
        logInfo("Поиск конкурсов.")
        contests = findContests(spbuSite)  # { contestId }
        logInfo("Найдено конкурсов: %d." % len(contests))

    contestLinks = addPrefixLinkToContests(spbuSite, contests)

    linkToAbits = findContestListsAsync(contestLinks)  # contestPage: { abit }

    logInfo("Обработано конкурсов: %d." % len(linkToAbits))
    logInfo("Найдено записей: %d. Готово." % sum(map(len, linkToAbits.values())))

    for saveMethod in saveMethods:
        saveMethod(linkToAbits, saveDir)
    logInfo("Сохранено.")
