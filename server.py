import socket
import sys

PORT_DEFAULT = 50007

ROLE_NULL =    200000
ROLE_CAPTAIN = 200001
ROLE_WEAPONS = 200002
ROLE_SHIELDS = 200003

def get_clients(server_soc):
	print server_soc

	rolenames = ["CAPTAIN", "WEAPON", "SHIELDS"]
	clients = []

	while len(clients) < 3:
		newconn, newaddr = server_soc.accept()
		print "new connection recieved, setting as", rolenames[len(clients)]
		clients.append( {
			"role":ROLE_NULL + len(clients) + 1,
			"conn":newconn ,
			"addr":newaddr
			}
			 )
		newconn.send(ROLE_NULL + len(clients))

	return clients

def alert_disconnect(clients):
	for client in clients:


if __name__ == "__main__":
	#asumed args is HOSTNAME [SOCKET]

	port = PORT_DEFAULT

	if len(sys.argv)<=1 or len(sys.argv)>2:
		print "\tformat is 'python server.py [SOCKET]'"
		print "\t[SOCKET] defaults to", PORT_DEFAULT
		sys.exit()
	elif len(sys.argv) == 2:
		port = int(sys.argv[1])

	#establish server
	print "Starting server on port %d"%(port)
	server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_soc.bind((socket.gethostname(), port))
	server_soc.listen(3)

	#getting connections
	clients = get_clients(server_soc)

	#notify all clients that it's time to 