import time
import zmq
import math

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
	#  Wait for next request from client
	mess = socket.recv()

	#  Do some 'work'
	time.sleep(1)

	file = open("file",'ab')
	file.write(mess)

	socket.send(b"mensaje recibido")