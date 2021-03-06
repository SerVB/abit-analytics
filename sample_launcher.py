# encoding=utf-8

# ----- РАНХиГС -----

# Запустить парсинг бакалавриата РАНХиГС для конкретного филиала
import ranepa_bach; ranepa_bach.main(department="Московский (ПК Академии)")

# Запустить парсинг бакалавриата РАНХиГС для всех филиалов
import ranepa_bach; ranepa_bach.main()

# Запустить парсинг магистратуры РАНХиГС для конкретного филиала
import ranepa_mag; ranepa_mag.main(department="Дальневосточный институт управления - филиал")

# Запустить парсинг магистратуры РАНХиГС для всех филиалов
import ranepa_mag; ranepa_mag.main()

# ----- СПбГУ -----

# Запустить парсинг бакалавриата СПбГУ для всех конкурсов
# (чтобы получить полный список, нужно сделать порядка десяти тысяч запросов, поэтому это займет долгое время)
import spbu_bach; spbu_bach.main()

# Запустить парсинг бакалавриата СПбГУ для конкретных конкурсов (точные относительные ссылки)
import spbu_bach; spbu_bach.main(contests={"list_7e08ab64-cc9f-4bf4-bf46-76778f361583.html"})

# Запустить парсинг магистратуры СПбГУ для всех конкурсов
# (полный список конкурсов находится на одной странице, список получается быстро)
import spbu_mag; spbu_mag.main()

# Запустить парсинг магистратуры СПбГУ для конкретных конкурсов (точные относительные ссылки)
import spbu_mag; spbu_mag.main(contests={"list1_1_2_3151_1024_0.html"})

# ----- РГГУ -----

# Запустить парсинг магистратуры РГГУ для всех конкурсов
import rggu_mag; rggu_mag.main()

# ----- МГУ -----

# Запустить парсинг магистратуры МГУ для всех конкурсов
import msu_mag; msu_mag.main()
