from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep


def makeDummySoup():
    return BeautifulSoup("dummy html", "html.parser")


def makeSoup(url):
    try:
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
        req = Request(url, headers={'User-Agent': userAgent})  # На всякий случай пробуем маскироваться
        html = urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except HTTPError as e:
        print("При попытке открыть %s произошла ошибка %s..." % (url, e))
        return makeDummySoup()
    except URLError as e:
        print("При попытке открыть %s произошла ошибка %s. Ждем и пробуем дальше!" % (url, e))
        sleep(10)
        return makeSoup(url)


print("--- СПбГУ -----")
SPBU_SITE = "https://cabinet.spbu.ru/Lists/1k_EntryLists/"

soup = makeSoup(SPBU_SITE)

# Поиск всех ID всех абитуриентов:
# Поиск всех ячеек -- тегов вида <td id="f585917a-d7af-499d-8299-e83624aeb8b7" ...>
abitIds = set()
for td in soup.find_all("td"):
    if td.has_attr("id"):
        abitIds.add(td["id"])

abitCount = len(abitIds)
print("Найдено абитуриентов: %d." % abitCount)

rowCount = len(soup.find_all("tr"))
if abitCount != rowCount - 1:
    print("Подозрительно: строчек в таблице %d, а должно быть %d!" % (rowCount, abitCount + 1))

# Поиск всех конкурсов:
# Для каждого студента находим ссылки вида
# "list_fe7557c2-2287-4559-8006-238597740d08.html#b30a2f1e-b2be-4c7a-9951-71848bad5274"
# и отбрасываем якорную часть
abitContests = dict()  # abitId: { contestId }
CONTESTS_SITE = "https://cabinet.spbu.ru/Lists/1k_EntryLists/data/%s.txt"


def extractContests(abitId):
    abitContests[abitId] = set()
    soup = makeSoup(CONTESTS_SITE % abitId)
    for a in soup.find_all("a"):
        if a.has_attr("href"):
            contestPage = a["href"]
            abitContests[abitId].add(contestPage[:contestPage.find("#")])


abitTasks = set()
for abitId in abitIds:
    task = Thread(target=extractContests, args=(abitId,))
    abitTasks.add(task)
    task.start()

for task in abitTasks:
    task.join()

contests = set()

for abitId, abitContest in abitContests.items():
    for contest in abitContest:
        contests.add(contest)

contestCount = len(contests)
print("Найдено конкурсов: %d." % contestCount)
