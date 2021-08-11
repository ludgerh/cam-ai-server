from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from pickle import loads
from c_client.c_tools import djconf

class c_stream():

  def __init__(self, port):
    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.connect(("localhost", port))
    print('Connected', port)

class c_stream_dict(dict):

  def __init__(self):
    super().__init__()
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(("localhost", djconf.getconfigint('str_ini_port',4444)))
    while True:
      message = s.recv(4)
      if message == b'':
        sleep(0.01)
      else:
        if message == b'Done':
          break
        else:
          oneport = int.from_bytes(message, byteorder='big')
          self[oneport] = c_stream(oneport)
    s.close()
    print('c_stream_clients', self)
