# encoding=utf-8

from common_json import DEFAULT_SAVE_METHODS

from spbu_main import parseSpbu

SPBU_SITE = "https://cabinet.spbu.ru/Lists/1k_EntryLists/index_comp_groups.html"


def main(contests=None, saveMethods=DEFAULT_SAVE_METHODS):
    parseSpbu(contests, saveMethods, SPBU_SITE, "СПбГУ (Бакалавриат)", "spbu-bach")


if __name__ == "__main__":
    main()
