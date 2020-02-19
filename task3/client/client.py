import zmq

context = zmq.Context()

#  Socket to talk to server
print("Conectando con el servidor...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# read file
file = open("file1m", "rb")

print("Enviando archivo...")
while True:
	for line in file:
		socket.send(line)
		result = socket.recv()
	break

print("Archivo enviado")