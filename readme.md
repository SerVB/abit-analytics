# Сбор данных о поступающих в ВУЗы России
Летняя учебная практика в 2018 г.

**Руководитель**: Паринов Андрей Андреевич.

## Технологии
- *Python 3*.
- Библиотеки *urllib*, *BeautifulSoup 4*, *threading*, *logging*.

## Собираемые данные
Следующие данные сохраняются в python-словарь и в json файл:

Признак | Название | Тип
--- | --- | ---
ФИО абитуриента |
Дата рождения |
Дата подачи документов |
Факультет |
Направление подготовки / Специальность |
Образовательная программа |
Форма обучения (*бюджет* или *коммерция*?) |
Баллы ЕГЭ (*по предметам* и *сумма*) |
Индивидуальные достижения (*сумма*) |
Аттестат (*подлинник* или *копия*?) |
Форма обучения (*очная* или *очно-заочная*?) |
Тип отбора (*общий конкурс* или *прием по квоте* или *прием без вступительных испытаний*?) |

Некоторых данных может не быть.

## Отслеживаемые ВУЗы
### СПбГУ
Списки поступающих находятся на странице <https://cabinet.spbu.ru/Lists/1k_EntryLists/>, где у каждого поступающего есть ссылки на таблицы с конкурсами. Работа скрипта:
- Строится список поступающих.
- Вытаскиваются конкурсы для каждого поступающего (асинхронно).
- Список конкурсов объединяется.