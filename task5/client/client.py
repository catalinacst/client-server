import zmq
import hashlib
import sys
import json
from os import listdir

# 5560

class Client():
	def __init__(self, ip = "localhost", port = "5560", ip_general = "localhost", port_general = "5555"):
		self.ip = ip
		self.port = port
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ) # realiza peticion
		self.sizechunk = 20 * 1024 * 1024 # 20MB
		self.ip_general = ip_general
		self.port_general = port_general

	def view_info(self):
		print("upload - download")
		print("help -- show options\n")

	def download_file(self, id_hash, hashname, namefile, ip, port):
		self.socket.connect("tcp://{}:{}".format(ip, port)) # known server
		self.socket.send_multipart(["download_file".encode(), str(id_hash).encode(), hashname.encode()])
		data = self.socket.recv_multipart()
		self.socket.disconnect("tcp://{}:{}".format(ip, port)) # known server
		ans = data[0].decode()
		if(ans == "no"):
			data_next = json.loads(data[1].decode())
			self.download_file(id_hash, hashname, namefile, data_next["ip"], data_next["port"])
		else:
			chunk = data[1]
			file = open("recv_" + str(self.port) + "/" + namefile, "ab")
			file.write(chunk)
			file.close()

	def verify_download_file(self, hashname):
		file = open("recv_" + str(self.port) + "/" + hashname, "rt")
		file.seek(0)
		lines = file.readlines()
		sizelines = len(lines)
		i = 1
		namefile = ''
		for line in lines:
			if(i == 1):
				namefile = line.rstrip('\n')
			else:
				ans = "no"
				if(i >= sizelines):
					break
				hashpart = line.rstrip('\n')
				id_hash = int(hashpart, 16)
				self.download_file(id_hash, hashpart, namefile, self.ip_general, self.port_general)
				print("downloading part ", i, "...")
			i = i + 1
		file.close()

	def download_data(self, hashname, ip, port):
		self.socket.connect("tcp://{}:{}".format(ip, port)) # known server
		self.socket.send_string(hashname)
		ok, chunk = self.socket.recv_multipart()
		self.socket.disconnect("tcp://{}:{}".format(ip, port)) # known server
		file = open("recv_" + str(self.port) + "/" + hashname, "wb")
		file.write(chunk)
		file.close()

	def verify_download_data(self, hashname, ip, port):
		self.socket.connect("tcp://{}:{}".format(ip, port)) # known server
		id_hash = int(hashname, 16)
		self.socket.send_multipart(["verify_download_data".encode(), str(id_hash).encode()])
		data = self.socket.recv_multipart()
		self.socket.disconnect("tcp://{}:{}".format(ip, port)) # known server
		ans = data[0].decode()
		if(ans == "no"):
			data_next = json.loads(data[1].decode())
			self.verify_download_data(hashname, data_next["ip"], data_next["port"])
		else:
			self.download_data(hashname, ip, port)

	def upload_file(self, hashpart, chunk, ip, port):
		self.socket.connect("tcp://{}:{}".format(ip, port)) # known server
		id_hash = int(hashpart, 16)
		self.socket.send_multipart(["upload_file".encode(), str(id_hash).encode(), str(hashpart).encode(), chunk])
		data = self.socket.recv_multipart()
		self.socket.disconnect("tcp://{}:{}".format(ip, port)) # known server
		ans = data[0].decode()
		if(ans == "no"):
			data_next = json.loads(data[1].decode())
			self.upload_file(hashpart, chunk, data_next["ip"], data_next["port"])

	def upload_data_file(self, filename):
		print("uploading datafile...")
		file = open("recv_" + str(self.port) + "/" + filename, "rb")
		flat = 1
		hash_filename = ''
		while True:
			chunk = file.read(self.sizechunk)
			if not chunk:
				hash_filename = str(hashall.hexdigest())
				break
			if(flat == 1):
				hashall = hashlib.sha1(chunk)
				flat = 0
			else:
				hashall.update(chunk)
			hashpart = hashlib.sha1(chunk).hexdigest()
			self.upload_file(hashpart, chunk, self.ip_general, self.port_general)
		file.close()
		print("done!")
		return hash_filename

	def split_file(self, filename):
		file = open(filename, "rb")
		flat = 1
		file_hash = open("recv_" + str(self.port) + "/data_" + filename, 'wt')
		file_hash.write(filename + "\n")
		i = 1
		while True:
			chunk = file.read(self.sizechunk)
			if not chunk:
				file_hash.write(str(hashall.hexdigest()) + "\n")
				file_hash.close()
				break
			if(flat == 1):
				hashall = hashlib.sha1(chunk)
				flat = 0
			else:
				hashall.update(chunk)
			hashpart = hashlib.sha1(chunk).hexdigest()
			file_hash.write(hashpart + "\n")
			self.upload_file(hashpart, chunk, self.ip_general, self.port_general)
			print("uploading part " + str(i))
			i = i + 1
		file.close()
		return "data_" + filename

	def run(self):
		self.view_info()
		while True:
			print("Client running on port {}".format(self.port))
			print("waiting command...")
			action = input()
			print("action: " + action)
			if(action == "upload"):
				print("waiting filename:")
				filename = input()
				data_filename = self.split_file(filename)
				hash_filename = self.upload_data_file(data_filename)
				print("file uploaded: ", hash_filename)
			elif(action == "download"):
				print("waiting filename:")
				hashname = input()
				data = self.verify_download_data(hashname, self.ip_general, self.port_general)
				self.verify_download_file(hashname)
			elif(action == "help"):
				self.view_info()
			else:
				print(action, "command 404, try again")



ip = sys.argv[1]
port = sys.argv[2]
ip_general = sys.argv[3]
port_general = sys.argv[4]
client = Client(ip, port, ip_general, port_general)
client.run() # datos del proxy