from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from time import sleep
import logging
import json
import ssl

LOGGING_FORMAT = "%(asctime)s:::%(levelname)s:::%(message)s"
LOGGING_FILE = "lastLog.txt"
logging.basicConfig(handlers=[logging.FileHandler(LOGGING_FILE, "w", "utf-8")],
                    format=LOGGING_FORMAT,
                    level=logging.INFO)


# Логирует ошибку в консоль и в файл
def logError(message):
    print("!Ошибка!", message)
    logging.error(message)


# Логирует предупреждение в консоль и в файл
def logWarning(message):
    print("!Предупреждение!", message)
    logging.warning(message)


# Логирует сообщение в консоль и в файл
def logInfo(message):
    print(message)
    logging.info(message)


# Делает пустой суп
def makeDummySoup():
    return BeautifulSoup("dummy html", "html.parser")


# Делает суп по ссылке.
# Если не удается сделать за maxTimes раз, сообщает о неудаче и отдает пустой суп
def makeSoup(url, title=None, time=1, maxTimes=3):
    if time > maxTimes:
        message = "Не смог получить доступ к странице %s уже много раз (%d). Больше не буду пытаться."
        if title is None:
            message %= (url, maxTimes)
        else:
            message %= ("%s (%s)" % (url, title), maxTimes)
        logWarning(message)
        return makeDummySoup()

    try:
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
        req = Request(url, headers={"User-Agent": userAgent})
        html = urlopen(req, context=ssl._create_unverified_context()).read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except (HTTPError, URLError) as e:
        message = "При попытке открыть %s произошла ошибка %s. Жду и пробую дальше! " \
                  "Осталось попыток: %d."
        remainingTimes = maxTimes - time
        if title is None:
            message %= (url, e, remainingTimes)
        else:
            message %= ("%s (%s)" % (url, title), e, remainingTimes)
        logWarning(message)
        if remainingTimes >= 1:
            sleep(1)
        return makeSoup(url, title=title, time=time + 1, maxTimes=maxTimes)


logInfo("----- РАНХиГС -----")
RANEPA_ROOT = "https://lk.ranepa.ru/pk/list.php"
# RANEPA_SITE = "https://lk.ranepa.ru/pk/list.php?FT=1&FL=0"  # Почему не используем эту ссылку?
RANEPA_SITE = "https://lk.ranepa.ru/pk/list.php?FT=1&FL=0&FK=&FC=&FB=&FO=&F1=3dfc1680-5eff-4887-a318-288990d0e055"

soup = makeSoup(RANEPA_SITE)

specialities = dict()  # {specName: link}

for table in soup.find_all("table"):
    if table.has_attr("class") and "ranepa-table" in table["class"]:
        for tbody in table.find_all("tbody"):
            for a in tbody.find_all("a"):
                if a.has_attr("href"):
                    specialities[a.decode_contents().strip()] = RANEPA_ROOT + a["href"]

logInfo("Направлений найдено: " + str(len(specialities)))

specForm = dict()  # {specName: {form: link}}

formCount = 0

for specName, link in specialities.items():
    specForm[specName] = dict()
    soup = makeSoup(link)
    for table in soup.find_all("table"):
        if table.has_attr("class") and "ranepa-table" in table["class"]:
            for tbody in table.find_all("tbody"):
                for a in tbody.find_all("a"):
                    if a.has_attr("href"):
                        specForm[specName][a.decode_contents().strip()] = RANEPA_ROOT + a["href"]
                        formCount += 1

logInfo("Направлений, учитывая разделение на формы, найдено: " + str(formCount))

eduProg = dict()  # {specName: {form: {eduProg: link}}}

eduProgCount = 0

for specName, form in specForm.items():
    eduProg[specName] = dict()
    for formName, link in form.items():
        eduProg[specName][formName] = dict()
        soup = makeSoup(link)
        for table in soup.find_all("table"):
            if table.has_attr("class") and "ranepa-table" in table["class"]:
                for tbody in table.find_all("tbody"):
                    for a in tbody.find_all("a"):
                        if a.has_attr("href"):
                            eduProg[specName][formName][a.decode_contents().strip()] = RANEPA_ROOT + a["href"]
                            eduProgCount += 1
                            logInfo(specName + "|" + formName + "|" + a.decode_contents().strip())

logInfo("Направлений, учитывая разделение на формы и на ОП, найдено: " + str(eduProgCount))

ans = list()

pageCount = 0

for specName, form in eduProg.items():
    for formName, prog in form.items():
        for eduProg, link in prog.items():
            soup = makeSoup(link)
            pageCount += 1
            logInfo(str(pageCount) + "/" + str(eduProgCount))
            for section in soup.find_all("section"):
                if 'style="text-align:center">Список пуст</td>' in section.decode_contents():
                    continue
                if section.has_attr("id") and section["id"] in ("list_budget", "list_contract"):
                    fio = -42
                    status = -42
                    sum = -42
                    id = -42
                    preim = -42  # subjects: [id + 1, preim)
                    original = -1

                    for idx, td in enumerate(section.find_all("thead")[0].find_all("th")):
                        contents = td.decode_contents().strip()
                        if "ФИО" in contents:
                            fio = idx
                        elif "Статус" in contents:
                            status = idx
                        elif "Сумма конкурсных баллов" in contents:
                            sum = idx
                        elif "Сумма баллов по индивидуальным достижениям" in contents:
                            id = idx
                        elif "Преимущественное право" in contents:
                            preim = idx

                    assert -42 not in (fio, status, sum, id, preim)

                    subjectsCount = preim - (id + 1)
                    subjects = list(map(lambda x: x.find(text=True).strip(),
                                        section.find_all("thead")[0].find_all("th")[id + 1:preim]))

                    for tr in section.find_all("tbody")[0].find_all("tr"):
                        abit = dict()
                        abit["specialty"] = specName
                        abit["eduProg"] = eduProg
                        abit["onlyInWalls"] = formName
                        abit["forMoney"] = section["id"] == "list_contract"

                        tds = tr.find_all("td")

                        abit["abitName"] = tds[fio].find(text=True).strip()
                        abit["contestType"] = tds[status].find(text=True).strip()
                        abit["grades"] = dict()
                        try:
                            abit["grades"]["sum"] = int(tds[sum].find(text=True).strip())
                        except ValueError:
                            abit["grades"]["sum"] = None
                        for idx, subj in enumerate(subjects):
                            try:
                                abit["grades"][subj] = int(tds[id + 1 + idx].find(text=True).strip())
                            except ValueError:
                                abit["grades"][subj] = None
                        abit["extraBonus"] = int(tds[id].find(text=True).strip())
                        abit["original"] = tds[original].find(text=True).strip() == "Оригинал"

                        ans.append(abit)

ans = dict(enumerate(ans))

logInfo("Словарь создан")

with open("data-ranepa.json", "w", encoding="utf-8") as f:
    print(json.dumps(ans, ensure_ascii=False, indent=2), file=f)  # TODO: параметры JSON норм?
    logInfo("JSON записан")
