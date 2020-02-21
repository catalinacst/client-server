import time
import zmq
import hashlib
from os import listdir

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
	# recibir la accion
	print("Servidor Escuchando")
	action = socket.recv()
	action = action.decode('utf-8')
	socket.send(b"Accion Recibida")

	# validar las acciones
	if action == 'upload':
		#  Wait for next request from client
		filename, content, hashingclient = socket.recv_multipart()
		print("Recibiendo Archivo...")
		hashingserver = hashlib.md5(content).digest()

		if hashingclient == hashingserver:
			file = open("files/" + filename.decode(), 'wb')
			file.write(content)
			file.close()
			socket.send(b"Archivo Recibido")
			print("Archivo Correcto")
		else:
			socket.send(b"Archivo Corrupto")
			print("Archivo Corrupto")
	elif action == 'list':
		print("Enviando Lista Archivos...")
		ok = socket.recv()
		listfiles = listdir("files/")
		socket.send_string("%s" % str(listfiles))
	elif action == 'download':
		i = 0
		print("Solicitud Descarga Archivo...")
		down_namefile = socket.recv_string()
		listfiles = listdir("files/")
		print(listfiles)
		count = 0
		for file in listfiles:
			namefile = down_namefile + ".part_1"
			if file == namefile:
				print("Si se encontro el archivo...")
				i = 1
				while True:
					namefile = down_namefile + ".part_" + str(i)
					count = count + 1
					for file in listfiles:
						if file == namefile:
							i = i + 1
							break
					if count > len(listfiles):
						break
				break
		if i == 0:
			socket.send_string("%s" % "0")
		else:
			socket.send_string("%s" % str(i - 1))

		sizechunk = 2 * 1024 * 1024
		part = 1
		while True:
			print("ingreso while server")
			ok = socket.recv()
			namefile = down_namefile + ".part_" + str(part)
			if namefile in listfiles:
				file = open("files/" + namefile, "rb")
				chunk = file.read(sizechunk)
				part = part + 1
				if not chunk:
					break
				hashing = hashlib.md5(chunk).digest()
				# send filename, content and hash
				flat = "1"
				socket.send_multipart([down_namefile.encode(), chunk, hashing, flat.encode('utf-8')])
				file.close()
			else:
				flat = "0"
				socket.send_multipart([down_namefile.encode(), chunk, hashing, flat.encode('utf-8')])
				break
