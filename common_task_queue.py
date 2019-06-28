# encoding=utf-8

from queue import Queue
from threading import Thread

# [(func, (args))]
taskQueue = Queue()


def _worker():
    while True:
        func, args = taskQueue.get()
        func(*args)
        taskQueue.task_done()


# Количество потоков-рабочих. 5 на моей машине работает без ошибок
MAX_WORKER_COUNT = 5


for i in range(MAX_WORKER_COUNT):
    thread = Thread(target=_worker, name="Worker %d/%d" % (i + 1, MAX_WORKER_COUNT), daemon=True)
    thread.start()
