import time
import zmq
import hashlib
from os import listdir

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
	# recibir la accion
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
		print("Solicitud Descarga Archivo...")
		down_namefile = socket.recv_string()
		# conocer cantidad de partes que tiene el archivo a descargar
		# file = open("files/" + down_namefile, "rb")
		socket.send(b"ok")
