import zmq
import hashlib
import sys
from os import listdir

# 5557

class Server():
	def __init__(self, ip, port, capacity):
		self.ip = ip
		self.port = port
		self.capacity = capacity
		self.context = zmq.Context()
		self.socketREQ = self.context.socket(zmq.REQ) # realiza peticion (register)
		self.socketREP = self.context.socket(zmq.REP) # espera peticion
		self.socketREP.bind("tcp://*:{}".format(self.port))

	def register(self, ip_proxy = "localhost", port_proxy = "5556"): # register server in proxy
		print("** registrando servidor **")
		self.ip_proxy = ip_proxy
		self.port_proxy = port_proxy
		self.socketREQ.connect("tcp://{}:{}".format(self.ip_proxy, self.port_proxy)) # ip -> localhost
		self.socketREQ.send_string("newserver")
		self.ok = self.socketREQ.recv_string()
		self.socketREQ.send_multipart([self.ip.encode(), self.port.encode(), self.capacity.encode()])
		self.ok = self.socketREQ.recv_string()
		print(self.ok)
		self.socketREQ.disconnect("tcp://{}:{}".format(self.ip_proxy, self.port_proxy)) # ip -> localhost

	def upload_file(self, part, content, hashingclient):
		print("** recibiendo archivo... parte: **" + part)
		self.hashingserver = hashlib.md5(content).digest()
		if hashingclient == self.hashingserver:
			self.file = open("files/" + str(part), 'wb')
			self.file.write(content)
			self.file.close()
			self.socketREP.send_string("archivo recibido")
		else:
			self.socketREP.send_string("archivo corrupto")

	def download_file(self, filename_down):
		self.listfiles = listdir("files/")
		self.sizechunk = 2 * 1024 * 1024
		if filename_down in self.listfiles:
			self.file = open("files/" + filename_down, "rb")
			self.chunk = self.file.read(self.sizechunk)
			self.socketREP.send(b"%s" % self.chunk)

	def listening(self):
		print("Servidor escuchando en el puerto {}".format(self.port))
		while True:
			action = self.socketREP.recv_string()
			self.socketREP.send_string("accion recibida")
			if action == 'upload':
				part, content, hashingclient = self.socketREP.recv_multipart()
				self.upload_file(part.decode(), content, hashingclient)
			if action == 'download':
				filename_down = self.socketREP.recv_string() # hash
				self.download_file(filename_down)

ip = sys.argv[1]
port = sys.argv[2]
capacity = sys.argv[3]
# print("ip: %s port: %s capacity: %s" % ip, port, capacity)
server = Server(ip, port, capacity)
server.register("localhost", "5556") # datos del proxy
server.listening()

