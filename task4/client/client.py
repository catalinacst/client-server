import zmq
import hashlib
import sys
import json
from os import listdir

# 5555

class Client():
	def __init__(self, ip = "localhost", port = "5555"):
		self.ip = ip
		self.port = port
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ) # realiza peticion
		self.sizechunk = 2 * 1024 * 1024 # 2MB

	def split_file(self, filename):
		self.part = 0
		self.file = open(filename, "rb")
		while True:
			self.chunk = self.file.read(self.sizechunk)
			self.part = self.part + 1
			if not self.chunk:
				break
			self.hashing = hashlib.md5(self.chunk).digest()
			self.filename_part = "part" + str(self.part)
			self.file_part = open("to_send/" + self.filename_part, 'wb')
			self.file_part.write(self.chunk)
			self.file_part.close()
		self.file.close()

	def up_files(self, filename, hash_server):
		self.servers = self.hash_server.get(filename)
		for server in self.servers:
			self.part = server[0]
			self.ip = server[1]
			self.port = server[2]
			self.file = open("to_send/" + self.part, "rb")
			self.chunk = self.file.read(self.sizechunk)
			self.hashing = hashlib.md5(self.chunk).digest()
			self.socket.connect("tcp://{}:{}".format(self.ip, self.port)) # ip -> localhost
			self.socket.send_string("upload")
			self.ok = self.socket.recv_string()
			self.socket.send_multipart([self.part.encode(), self.chunk, self.hashing])
			self.ok = self.socket.recv_string()
			print(self.ok)
			self.file.close()
			self.socket.disconnect("tcp://{}:{}".format(self.ip, self.port)) # ip -> localhost

	def down_files(self, filename, hash_server):
		for server in hash_server:
			self.part = server[0]
			self.ip = server[1]
			self.port = server[2]
			self.socket.connect("tcp://{}:{}".format(self.ip, self.port)) # ip -> localhost
			self.socket.send_string("download")
			self.ok = self.socket.recv_string()
			self.socket.send_string(self.part)
			content, hashingserver = self.socket.recv_multipart()
			self.hashingclient = hashlib.md5(content).digest()
			if self.hashingclient == hashingserver:
				self.file = open("recv/" + filename, 'ab')
				self.file.write(content)
			self.socket.disconnect("tcp://{}:{}".format(self.ip, self.port)) # ip -> localhost
		self.file.close()

	def listening(self, ip_proxy, port_proxy):
		print("Cliente en el puerto {}".format(self.port))
		print("Escriba el comando: upload - download")
		while True:
			action = input()
			if action == 'upload':
				self.socket.connect("tcp://{}:{}".format(ip_proxy, port_proxy)) # ip -> localhost
				self.socket.send_string(action)
				self.ok = self.socket.recv_string()
				# print("escriba el nombre del archivo a subir")
				# filename = input()
				self.filename = "file10m"
				self.split_file(self.filename)
				self.listfiles = listdir("to_send/")
				self.listfiles.sort()
				self.socket.send_multipart([self.filename.encode(), json.dumps(self.listfiles).encode('utf8')])
				self.hash_server = json.loads(self.socket.recv().decode('utf8'))
				self.socket.disconnect("tcp://{}:{}".format(ip_proxy, port_proxy)) # ip -> localhost
				self.up_files(self.filename, self.hash_server)
			if action == 'download':
				self.socket.connect("tcp://{}:{}".format(ip_proxy, port_proxy)) # ip -> localhost
				self.socket.send_string(action)
				self.ok = self.socket.recv_string()
				# print("escriba el nombre del archivo a descargar")
				# filename = input()
				self.filename = "file10m"
				self.socket.send_string(self.filename)
				self.hash_server = json.loads(self.socket.recv().decode('utf8'))
				self.socket.disconnect("tcp://{}:{}".format(ip_proxy, port_proxy)) # ip -> localhost
				# print(self.hash_server)
				self.down_files(self.filename, self.hash_server)


# ip = sys.argv[1]
# port = sys.argv[2]

client = Client()
client.listening("localhost", "5556") # datos del proxy