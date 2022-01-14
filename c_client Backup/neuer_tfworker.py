from multiprocessing import Process, Queue

class tf_worker(Process):

  def __init__(self, id):
    super().__init__()
    self.id = id
    self.fifoin = Queue()
    self.fifoout = Queue()

  def run(self):
    print(self.fifoin.get(), self.id)
    self.fifoout.put('XYZ')
