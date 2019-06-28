# encoding=utf-8

from common_json import DEFAULT_SAVE_METHODS

from spbu_main import parseSpbu

SPBU_SITE = "https://cabinet.spbu.ru/Lists/Mag_EntryLists/index_comp_groups.html"


def main(contests=None, saveMethods=DEFAULT_SAVE_METHODS):
    parseSpbu(contests, saveMethods, SPBU_SITE, "СПбГУ (Магистратура)", "spbu-mag")


if __name__ == "__main__":
    main()
