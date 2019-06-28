# encoding=utf-8

from typing import List

from common_json import DEFAULT_SAVE_METHODS
from spbu_main import parseSpbu

SPBU_SITE = "https://cabinet.spbu.ru/Lists/1k_EntryLists/index_comp_groups.html"


def main(contests: List[str] = None, saveMethods=DEFAULT_SAVE_METHODS) -> None:
    parseSpbu(contests, saveMethods, SPBU_SITE, "СПбГУ (Бакалавриат)", "spbu-bach")


if __name__ == "__main__":
    main()
