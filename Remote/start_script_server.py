import socket

"""
Server to start script on Flax' computer

"""





sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.gethostname(), 62111))

sock.listen(5)


