import zmq
import hashlib
import sys
from os import listdir

class Server():
	def __init__(self, ip, port, capacity):
		self.ip = ip
		self.port = port
		self.capacity = capacity
		self.context = zmq.Context()
		self.socketREQ = self.context.socket(zmq.REQ) # realiza peticion (register)
		self.socketREP = self.context.socket(zmq.REP) # espera peticion
		self.socketREP.bind("tcp://*:{}".format(self.port))

	def register(self): # register server in proxy
		self.socketREQ.connect("tcp://{}:{}".format(self.ip, self.port)) # ip -> localhost
		self.socketREQ.send_multipart([self.ip, self.port, self.capacity])
		self.ok = socketREQ.recv_string()

	def upload_file(self, filename, content, hashingclient):
		print("recibiendo archivo...")
		self.hashingserver = hashlib.md5(content).digest()
		if hashingclient == self.hashingserver:
			self.file = open("files/" + hashingclient, 'wb')
			self.file.write(content)
			self.file.close()
			socketREP.send(b"archivo recibido")
		else:
			socketREP.send(b"archivo corrupto")

	def download_file(self, filename_down):
		self.listfiles = listdir("files/")
		self.sizechunk = 2 * 1024 * 1024
		if filename_down in self.listfiles:
			self.file = open("files/" + filename_down, "rb")
			self.chunk = self.file.read(self.sizechunk)
			self.socketREP.send(b"%s", self.chunk)

	def listening(self):
		print("Servidor escuchando en el puerto {}".format(self.port))
		while True:
			action = self.socketREP.recv()
			action = action.decode('utf-8')
			self.socketREP.send(b"accion recibida")
			if action == 'upload':
				filename, content, hashingclient = socketREP.recv_multipart()
				self.upload_file(filename, content, hashingclient)
			if action == 'download':
				filename_down = socketREP.recv_string() # hash
				self.download_file(filename_down)



ip = sys.argv[1]
port = sys.argv[2]
capacity = sys.argv[3]
print("ip: %s port: %s capacity: " % ip, port, capacity)
server = Server(ip, port, capacity)
server.register()
server.listening()

