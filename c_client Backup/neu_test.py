from neuer_tfworker import tf_worker

mytf = tf_worker(0)
mytf.start()
mytf.fifoin.put('ABC')
print(mytf.fifoout.get())
