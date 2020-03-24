from os import listdir
import sys

port = sys.argv[1]
l = int(sys.argv[2])
r = int(sys.argv[3])
especial = int(sys.argv[4])

hashes = listdir(str(port) + "/")
for hashh in hashes:
	id_hash = int(hashh, 16)
	if(especial == 1):
		if(id_hash <= l or id_hash > r):
			print(hashh, "ok")
		else:
			print(hashh, "no")
	else:
		if(id_hash > l and id_hash < r):
			print(hashh, "ok")
		else:
			print(hashh, "no")