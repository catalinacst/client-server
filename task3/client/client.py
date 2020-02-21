import zmq
import hashlib

context = zmq.Context()

#  Socket to talk to server
print("Conectando con el servidor...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# 2MB
sizechunk = 2 * 1024 * 1024

# read file
namefile = "file10m"
file = open(namefile, "rb")
part = 0

print("Escriba el comando: upload - list - download")
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
		# send action
		socket.send(b"%s" % action.encode('utf-8'))
		ok = socket.recv()

		# recibir por teclado nombre archivo
		print("Escriba el nombre del archivo a descargar:")
		down_namefile = input()
		socket.send_string("%s" % down_namefile)
		ans = socket.recv_string()
		if ans == 0:
			print("No se encontro el archivo")
		else:
			print("Se encontraron " + ans + " partes")
		while True:
			print("ingreso while cliente")
			socket.send(b"solicitud partes")
			filename, content, hashingserver, flat = socket.recv_multipart()
			flat = flat.decode('utf-8')
			if flat == "1":
				print("ingreso flat cliente")
				hashingclient = hashlib.md5(content).digest()
				if hashingclient == hashingserver:
					file = open("recv/" + filename.decode(), 'ab')
					file.write(content)
					file.close()
					print("Archivo Correcto")
				else:
					print("Archivo Corrupto")
			else:
				break
		break
if action == 'upload':
	file.close()


