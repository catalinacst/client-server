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
	ope = socket.recv()
	ope = ope.decode('utf-8')
	print("Recibiendo operacion: %s" % ope)
	print("Calculando...")
	#  Do some 'work'
	time.sleep(1)

	ope = ope.split()
	if (len(ope) == 3):
		if(ope[1] == '+'):
			result = int(ope[0]) + int(ope[2])
		if(ope[1] == '-'):
			result = int(ope[0]) - int(ope[2])
		if(ope[1] == '/'):
			result = int(ope[0]) / int(ope[2])
		if(ope[1] == '*'):
			result = int(ope[0]) * int(ope[2])
		if(ope[1] == '^'):
			result = math.pow(int(ope[0]), int(ope[2]))
	else:
		if(len(ope) == 2):
			if(ope[0] == 'raiz'):
				result = math.sqrt(int(ope[1]))
	# print("El resultado es %s" % result)

	print("Resultado Enviado")
	result = str(result)
	#  Send reply back to client
	socket.send(b"%s" % result.encode('utf-8'))