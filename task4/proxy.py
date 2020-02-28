import zmq
import hashlib
import sys
import json

# 5556

class Proxy():
	def __init__(self, port):
		self.port = port
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.socket.bind("tcp://*:{}".format(self.port))
		self.serverslist = [] # [ip, port, capacity]
		self.hash_servers_general = {} # {filename: [hash, ip, port]}

	def register_nserver(self, ip, port, capacity):
		self.serverslist.append([ip, port, capacity])

	def upload_file(self, filename, hashes):
		self.weight = 2 # 2MB
		self.hash_servers_specific = {} # {filename: [hash, ip, port]}
		self.hash_servers_specific[filename] = []
		self.hash_servers_general[filename] = []
		# load balancing
		i = 0
		cantservers = len(self.serverslist)
		for hashh in hashes:
			if i == cantservers - 1:
				i = 0
			else:
				i = i + 1
			save = 0
			while save == 0:
				capacity = self.serverslist[i][2] # server capacity
				if self.weight < int(capacity):
					self.serverslist[i][2] = int(self.serverslist[i][2]) - self.weight
					ip = self.serverslist[i][0] # ip server
					port = self.serverslist[i][1] # port server
					self.hash_servers_specific[filename].append([hashh, ip, port])
					self.hash_servers_general[filename].append([hashh, ip, port])
					save = 1
		print("Balanceo de Cargas")
		print(self.hash_servers_specific)
		return self.hash_servers_specific

	def download_file(self, filename):
		if self.hash_servers_general.has_key(filename) == True:
			data = listone.get(filename)
		return data

	def listening(self):
		print("Proxy escuchando en el puerto {}".format(self.port))
		while True:
			action = self.socket.recv_string()
			self.socket.send_string("accion recibida")
			# analizar opciones
			if action == 'newserver':
				ip, port, capacity = self.socket.recv_multipart()
				self.register_nserver(ip.decode(), port.decode(), capacity.decode())
				self.socket.send_string("** servidor registrado **")
				print("Servidores Conectados " + str(self.serverslist))
			if action == 'upload':
				# hashes (partes) weights (peso de las partes siempre es 2)
				print("cliente conectado")
				data = self.socket.recv_multipart()
				filename = data[0]
				hashes = json.loads(data[1].decode('utf8'))
				hashes_server = self.upload_file(filename.decode(), hashes)
				self.socket.send(json.dumps(hashes_server).encode('utf8'))
			if action == 'download':
				filename = self.socket.recv_multipart()
				hashes_server = self.download_file(filename)
				self.socket.send(hashes_server)
			# if action == 'list': listar todos las keys de hash_servers_general

port = sys.argv[1]
proxy = Proxy(port)
proxy.listening()

		