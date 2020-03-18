import zmq
import hashlib
import sys
import json
import getmac # get_mac
import random
import string
from os import listdir

# 5555 general

class Server():
	def __init__(self, ip, port, ip_general = "localhost", port_general = "5555"):
		self.ip = ip 
		self.port = port
		self.context = zmq.Context()
		self.socketREQ = self.context.socket(zmq.REQ) # realiza peticion
		self.socketREP = self.context.socket(zmq.REP) # espera peticion
		self.socketREP.bind("tcp://*:{}".format(self.port))
		self.sizechunk = 2 * 1024 * 1024 # 2MB
		self.ip_general = ip_general
		self.port_general = port_general
		self.ide = None
		self.data_prev = {} # ip, port
		self.data_next = {} # ip, port
		self.range_left = None
		self.med_left = None
		self.med_right = None
		self.range_right = None
		self.done = None
		self.special_node = None

	def set_id(self):
		mac = getmac.get_mac_address()
		ran = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
		hasid = hashlib.sha1((mac + ran).encode()).hexdigest()
		self.ide = int(hasid, 16)

	def get_id(self):
		return self.ide

	def update_data_prev(self, ip, port, ide = None):
		self.data_prev["ip"] = ip
		self.data_prev["port"] = port
		self.data_prev["ide"] = ide

	def update_data_next(self, ip, port, ide = None):
		self.data_next["ip"] = ip
		self.data_next["port"] = port
		self.data_next["ide"] = ide

	def update_ranges(self, range_left, range_right, med_right = None, med_left = None):
		# [range_left, med_right] U [med_left, range_right]
		self.range_left = range_left
		self.med_right = med_right
		self.med_left = med_left
		self.range_right = range_right

	def verify_init(self): # first server
		if(self.ip_general == self.ip and self.port_general == self.port):
			self.update_data_prev(self.ip, self.port)
			self.update_data_next(self.ip, self.port)
			self.range_left = 0
			self.med_right = self.ide
			self.med_left = self.ide
			self.range_right = (2 ** 160) - 1
			self.special_node = 1
			self.done = 1
			self.write_json_info()

	def write_json_info(self):
			file = open("info_server/" + str(self.port), 'wt')
			file.write("ide:  " + str(self.ide) + "\n")
			file.write("ip_general:  " + str(self.ip_general) + "\n")
			file.write("port_general:  " + str(self.port_general) + "\n")
			file.write("ide:  " + str(self.ide) + "\n")
			file.write("data_prev:  " + str(self.data_prev) + "\n")
			file.write("data_next:  " + str(self.data_next) + "\n")
			file.write("range_left:  " + str(self.range_left) + "\n")
			file.write("med_right:  " + str(self.med_right) + "\n")
			file.write("med_left:  " + str(self.med_left) + "\n")
			file.write("range_right:  " + str(self.range_right) + "\n")
			file.write("done:  " + str(self.done) + "\n")
			file.write("special_node:  " + str(self.special_node) + "\n" + "\n")
			file.close()

	def add_node(self, data):
		ide_nserver = int(data[1].decode())
		ip_nserver = data[2].decode()
		port_nserver = data[3].decode()
		confirm = 0
		if(self.special_node == 1):
			if((ide_nserver >= self.range_left and ide_nserver <= self.med_right) or (ide_nserver > self.med_left and ide_nserver <= self.range_right)):
				confirm = 1
				if(ide_nserver < self.ide):
					self.special_node = 0
		elif(ide_nserver > self.range_left and ide_nserver <= self.range_right):
			confirm = 1
		old_data_prev = {}
		if(confirm == 1):
			old_data_prev["ip"] = self.data_prev["ip"]
			old_data_prev["port"] = self.data_prev["port"]
			self.update_data_prev(ip_nserver, port_nserver)
			if(self.special_node == 1):
				self.update_ranges(0, (2 ** 160) - 1, self.ide, ide_nserver) # range_left, range_right, med_right, med_left
			else:
				self.update_ranges(ide_nserver, self.ide)
			self.socketREP.send_multipart(["ok".encode('utf8'), json.dumps(old_data_prev).encode('utf8')])
		else:
			self.socketREP.send_multipart(["no".encode('utf8'), json.dumps(self.data_next).encode('utf8')])

	def add_me(self, ip, port, ide = None): # informacion del nuevo servidor
		self.socketREQ.connect("tcp://{}:{}".format(ip, port)) # first known server (other -> iterator server)
		print("connect success")
		self.socketREQ.send_multipart(["add_node".encode('utf8'), str(self.ide).encode('utf8'), str(self.ip).encode('utf8'), str(self.port).encode('utf8')])
		add_node_done = self.socketREQ.recv_multipart()
		if(add_node_done[0].decode('utf8') == "ok"): # action
			add_data_prev = json.loads(add_node_done[1].decode('utf8'))
			self.update_data_prev(add_data_prev["ip"], add_data_prev["port"]) # ip, port
			self.update_data_next(ip, port)
			self.socketREQ.disconnect("tcp://{}:{}".format(ip, port)) # known serverf
			self.socketREQ.connect("tcp://{}:{}".format(add_data_prev["ip"], add_data_prev["port"])) # connect server prev
			self.socketREQ.send_multipart(["update_data_next".encode('utf8'), str(self.ip).encode('utf8'), str(self.port).encode('utf8')]) # update_next de mi prev
			ide_pev = int(self.socketREQ.recv_string()) # identificador 1
			if(ide_pev < self.ide):
				self.update_ranges(ide_pev, self.ide)
			else:
				self.update_ranges(0, (2 ** 160) - 1, self.ide, ide_pev) # range_left, range_right, med_right, med_left
				self.special_node = 1
			self.socketREQ.disconnect("tcp://{}:{}".format(add_data_prev["ip"], add_data_prev["port"])) # disconnect server prev
		else:
			add_data_next = json.loads(add_node_done[1].decode('utf8'))
			self.add_me(add_data_next["ip"], add_data_next["port"]) # ip, port

	def view_info(self):
		print("get_(id, ranges, prev, next, state)")
		print("add_node - set_(id, prev, next)")
		print("help -- show options\n")

	def upload_file(self, hashpart, chunk):
		print("save hash: ", hashpart.decode())
		file = open(str(self.port) + "/" + hashpart.decode(), "wb")
		file.write(chunk)
		file.close()

	def download_data(self, hashname):
		file = open(str(self.port) + "/" + str(hashname), "rb")
		chunk = file.read(self.sizechunk)
		self.socketREP.send_multipart(["ok".encode(), chunk])

	def verify(self, id_hash):
		confirm = 0
		if(self.special_node == 1):
			if((id_hash >= self.range_left and id_hash <= self.med_right) or (id_hash > self.med_left and id_hash <= self.range_right)):
				confirm = 1
		elif(id_hash > self.range_left and id_hash <= self.range_right):
				confirm = 1
		return confirm

	def verify_download(self, id_hash):
		confirm = self.verify(id_hash)
		if(confirm == 1):
			self.socketREP.send_multipart(["ok".encode()])
			hashname = self.socketREP.recv_string()
			self.download_data(hashname)
		else:
			self.socketREP.send_multipart(["no".encode(), json.dumps(self.data_next).encode()])

	def verify_upload(self, id_hash, hashpart, chunk):
		confirm = self.verify(id_hash)
		if(confirm == 1):
			self.upload_file(hashpart, chunk)
			self.socketREP.send_multipart(["ok".encode()])
		else:
			self.socketREP.send_multipart(["no".encode(), json.dumps(self.data_next).encode()])

	def verify_file(self, id_hash, hashname):
		confirm = self.verify(id_hash)
		if(confirm == 1):
			hashname = hashname.decode()
			self.download_data(hashname)
		else:
			self.socketREP.send_multipart(["no".encode(), json.dumps(self.data_next).encode()])

	def listening(self):
		self.view_info()
		while True:
			self.write_json_info()
			print("Server listening on port {}".format(self.port))
			data = self.socketREP.recv_multipart()
			action = data[0].decode()
			print("action: " + action)
			if action == "add_node":
				self.add_node(data)
			elif action == "update_data_next":
				ip = data[1].decode('utf8')
				port = data[2].decode('utf8')
				self.update_data_next(ip, port)
				self.socketREP.send_string(str(self.get_id())) # identificador 1
			elif action == "upload_file":
				id_hash = int(data[1])
				hashpart = data[2]
				chunk = data[3]
				self.verify_upload(id_hash, hashpart, chunk)
			elif action == "verify_download_data":
				id_hash = int(data[1])
				self.verify_download(id_hash)
			elif action == "download_file":
				id_hash = int(data[1])
				hashname = data[2]
				self.verify_file(id_hash, hashname)
			elif action == "help":
				self.view_info()
			else:
				print(action, "command 404, try again")

	def processes(self):
		self.set_id()
		self.verify_init() # first server
		if(not self.done):
			self.add_me(self.ip_general, self.port_general)
			self.done = 1
			self.write_json_info()
		self.listening()

ip = sys.argv[1]
port = sys.argv[2]
ip_general = sys.argv[3]
port_general = sys.argv[4]
server = Server(ip, port, ip_general, port_general)
server.processes()

# def get_prev(self):
# 	return self.data_prev

# def get_next(self):
# 	return self.data_next

# def get_range_left(self):
# 	return self.range_left

# def get_range_right(self):
# 	return self.range_right

# def get_state(self):
# 	return self.done