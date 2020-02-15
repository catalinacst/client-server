#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Conectando con el servidor aritmetico")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

print("Escriba la operacion aritmetica que desea realizar")
print("Ejemplo, 3 + 2, 5 ^ 2")

#  Do 10 requests, waiting each time for a response
for request in range(1):
	numone = input()
	socket.send(b"%s" % numone.encode('utf-8'))
	ok = socket.recv()
	print(ok)

	ope = input()
	socket.send(b"%s" % ope.encode('utf-8'))
	ok = socket.recv()
	print(ok)

	numtwo = input()
	socket.send(b"%s" % numtwo.encode('utf-8'))
	ok = socket.recv()
	print(ok)

	socket.send(b"Deme resultado")
	#  Get the reply.
	result = socket.recv()
	result = result.decode('utf-8')
	print("Respuesta servidor %s" % result)