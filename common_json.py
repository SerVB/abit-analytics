# encoding=utf-8

import json
import os
import urllib.parse
from typing import Union, Dict

from common_logging import logInfo


def _writeJson(jsonData: Union[dict, list], dirName: str, fileName: str) -> None:
    dirName = "output/" + dirName

    if not os.path.exists(dirName):
        os.makedirs(dirName)

    fileName = "output/" + dirName + urllib.parse.quote_plus(fileName).replace("\\", "/")

    suffixName = fileName[fileName.rfind("/") + 1:]
    if len(suffixName) > 255:  # Ограничение Windows
        suffixName = suffixName[-255:]

    fileName = dirName + suffixName

    with open(fileName, "w", encoding="utf-8") as outputFile:
        print(json.dumps(jsonData, ensure_ascii=False, indent=2), file=outputFile)
        logInfo("JSON файл '%s' записан." % fileName)


def writeJsonPerPage(linkToAbits: Dict[str, dict], dirName: str) -> None:
    for link, abits in linkToAbits.items():
        _writeJson({"link": link, "abits": abits}, dirName, link + ".json")


def writeJsonPerUniversity(linkToAbits: Dict[str, dict], universityName: str) -> None:
    _writeJson(linkToAbits, "", universityName + ".json")


DEFAULT_SAVE_METHODS = (writeJsonPerUniversity,)
