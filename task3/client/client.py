import zmq
import hashlib

context = zmq.Context()

#  Socket to talk to server
print("Conectando con el servidor...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

sizechunk = 2 * 1024 * 1024

# read file
namefile = "file1m"
file = open(namefile, "rb")
part = 0

action = input()

if action == 'upload':
	print("Enviando archivo...")
elif action == 'list':
	print("Listando archivos...")
elif action == 'download':
	print("Descargando archivo...")

while True:
	if action == 'upload':
		socket.send(b"%s" % action.encode('utf-8'))
		ok = socket.recv()
		chunk = file.read(sizechunk)
		part = part + 1
		if not chunk:
			break
		hashing = hashlib.md5(chunk).digest()
		filename = namefile
		filename = filename + ".part_" + str(part)
		
		# send filename, content and hash
		socket.send_multipart([filename.encode(), chunk, hashing])

		result = socket.recv()
		print("Resultado: %s" % result)
		print("Archivo enviado")
	elif action == 'list':
		# send action
		socket.send(b"%s" % action.encode('utf-8'))
		ok = socket.recv()

		# send request
		socket.send(b"lista archivos")
		lenlistfiles = socket.recv_string()
		print(lenlistfiles)
		break
	elif action == 'download':
		socket.send(b"%s" % action.encode('utf-8'))
		ok = socket.recv()

		down_namefile = input()
		socket.send_string("%s" % down_namefile)
		ok = socket.recv()
		print(ok)
		break
if action == 'upload':
	file.close()


