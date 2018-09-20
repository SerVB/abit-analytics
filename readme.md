# Сбор данных о поступающих в ВУЗы России
Проект начался как летняя учебная практика в 2018 г.

**Руководитель**: Паринов Андрей Андреевич.

## Суть
[![Python 3](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Build status](https://travis-ci.org/SerVB/abit-analytics.svg?master)](https://travis-ci.org/SerVB/abit-analytics)

Методы для загрузки списков поступающих в отслеживаемые ВУЗы, парсинга списков поступающих и сохранение списков в формате JSON.

## Быстрый старт
- В [`sample_launcher.py`](sample_launcher.py) показаны возможные варианты запуска сбора данных о поступающих для каждого отслеживаемого ВУЗа.
- [`sample_launcher_all_mag.py`](sample_launcher_all_mag.py) запускает сбор данных о поступающих в магистратуру отслеживаемых ВУЗов (время выполнения порядка **10 минут**).
- [`sample_launcher_all_bach.py`](sample_launcher_all_bach.py) запускает сбор данных о поступающих в бакалавриат отслеживаемых ВУЗов (время выполнения порядка **40 минут**).
- [`sample_launcher_all_bach_precomputed.py`](sample_launcher_all_bach_precomputed.py) запускает сбор данных о поступающих в бакалавриат отслеживаемых ВУЗов (для СПбГУ используется полный по состоянию на 20.09.2018 список конкурсов; время выполнения порядка **20 минут**).

## Технологии
- *Python 3* и стандартные библиотеки.
- Сторонняя библиотека *BeautifulSoup 4* (зависимости также перечислены в [`requirements.txt`](requirements.txt)).
- *Travis CI*.

## Отслеживаемые ВУЗы
Описания расположены по ссылкам:
- СПбГУ ([бакалавриат](docs/spbu_bach.md), [магистратура](docs/spbu_mag.md)).
- РАНХиГС ([бакалавриат](docs/ranepa_bach.md), [магистратура](docs/ranepa_mag.md)).
- МГУ ([магистратура](docs/msu_mag.md)).
- РГГУ ([магистратура](docs/rggu_mag.md)).

## Общий код
Несколько методов использованы практически в каждом ВУЗе, поэтому образованы следующие файлы.

### Работа с Интернетом ([`common_html.py`](common_html.py))
- Методы для скачивания страницы из Интернета (если какая-то страница не отвечает, обращение к ней происходит до трех раз).
- Методы для работы с кодом Интернет-страницы.

### Логирование ([`common_logging.py`](common_logging.py))
- Методы для логирования в файл `lastLog.txt` и в консоль.

### Многопоточное выполнение ([`common_task_queue.py`](common_task_queue.py))
- Объект очереди задач, позволяющий добавлять задачи и ждать, пока все они не будут выполнены.

### Работа с JSON ([`common_json.py`](common_json.py))
- Методы для сохранения результирующих файлов (имеют сигнатуру `({ссылка: список_поступающих_по_ссылке}, название_вуза)`).

### Параметры сохранения JSON файлов ([`common_properties.py`](common_properties.py))
- Именованные константы.
