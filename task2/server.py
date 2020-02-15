#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import math

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
	#  Wait for next request from client
	numone = socket.recv()
	numone = numone.decode('utf-8')
	socket.send(b"ok")

	ope = socket.recv()
	ope = ope.decode('utf-8')
	socket.send(b"ok")

	numtwo = socket.recv()
	numtwo = numtwo.decode('utf-8')
	socket.send(b"ok")

	print("Recibiendo operacion:")
	print("Calculando...")
	
	#  Do some 'work'
	time.sleep(1)

	if(ope == '+'):
		result = int(numone) + int(numtwo)
	if(ope == '-'):
		result = int(numone) - int(numtwo)
	if(ope == '/'):
		result = int(numone) / int(numtwo)
	if(ope == '*'):
		result = int(numone) * int(numtwo)
	if(ope == '^'):
		result = math.pow(int(numone), int(numtwo))

	print("Resultado Enviado")
	result = str(result)
	flat = socket.recv()

	#  Send reply back to client
	socket.send(b"%s" % result.encode('utf-8'))