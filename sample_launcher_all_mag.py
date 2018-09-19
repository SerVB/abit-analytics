# encoding=utf-8

from common_json import writeJsonPerUniversity

import ranepa_mag; ranepa_mag.main(saveMethods=(writeJsonPerUniversity,))
import spbu_mag; spbu_mag.main(saveMethods=(writeJsonPerUniversity,))
import rggu_mag; rggu_mag.main(saveMethods=(writeJsonPerUniversity,))
import msu_mag; msu_mag.main(saveMethods=(writeJsonPerUniversity,))
