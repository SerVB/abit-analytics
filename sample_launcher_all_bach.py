# encoding=utf-8

from common_json import writeJsonPerUniversity

import ranepa_bach; ranepa_bach.main(saveMethods=(writeJsonPerUniversity,))
import spbu_bach; spbu_bach.main(saveMethods=(writeJsonPerUniversity,))
