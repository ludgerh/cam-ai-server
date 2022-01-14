from multiprocessing import Process, Queue, shared_memory
from .c_tfworker import tf_worker

clients_per_worker = 20

tf_w_nrs = {0 : (1, 3, ), }

tf_workers = {x[0]:tf_worker(x[0], clients_per_worker, x[1]) for x in tf_w_nrs.items()}
for i in tf_workers:
  tf_workers[i].inqueue = Queue()
  tf_workers[i].outqueues = {}
  for j in range(clients_per_worker):
    tf_workers[i].outqueues[j] = Queue()

  tf_workers[i].start()
