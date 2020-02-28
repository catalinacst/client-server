import zmq
import hashlib
import sys

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

	def upload_file(self, filename, hashes, weights):
		self.hash_servers_specific = {} # {filename: [hash, ip, port]}
		print(hashes)
		# load balancing
		i = 0
		cantservers = len(self.serverslist)
		for (hashh, weight) in zip(hashes, weights):
			if i == cantservers - 1:
				i = 0
			save = 0
			while save == 0:
				capacity = self.serverslist[i][2] # server capacity
				if capacity < weight:
					self.serverslist[i][2] = self.serverslist[i][2] - capacity
					ip = self.serverslist[i][0] # ip server
					port = self.serverslist[i][1] # port server
					self.hash_servers_specific[filename].append([hashh, ip, port])
					self.hash_servers_general[filename].append([hashh, ip, port])
					save = 1
				else:
					i = i + 1
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
			if action == 'uploadfile':
				# hashes (partes) weights (peso de las partes)
				filename, hashes, weights = self.socket.recv_multipart()
				hashes_server = self.upload_file(filename, hashes, weights)
				self.socket.send_string(hashes_server)
			if action == 'downloadfile':
				filename = self.socket.recv_multipart()
				hashes_server = self.download_file(filename)
				self.socket.send_string(hashes_server)
			# if action == 'list': listar todos las keys de hash_servers_general


port = sys.argv[1]
proxy = Proxy(port)
proxy.listening()

		