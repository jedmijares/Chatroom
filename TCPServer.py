from socket import *
import threading
import sys
import os

answer = input("Will you host? ")

if(answer == 'y'):

    serverPort = 12000
    activeConnections = []

    # represents communication with an active client
    class ClientSocket(threading.Thread):
        def __init__(self, socket, address):
            super().__init__()
            self.socket = socket
            self.address = address

        def run(self):
            while True:
                message = None
                message = (self.socket.recv(1024)).decode()
                if message:
                    for client in activeConnections:
                        if client != self:
                            client.socket.sendall(message.encode())

    # create TCP welcoming socket
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(("",serverPort))

    # server begins listening for incoming TCP requests
    serverSocket.listen(1)

    # # output to console that server is listening
    print ("The server is ready to receive... ")

    while True:
        # server waits for incoming requests; new socket created on return
        connectionSocket, address = serverSocket.accept()

        newConnection = ClientSocket(connectionSocket, address)
        newConnection.start()
        activeConnections.append(newConnection)

else: # client

    class Sender(threading.Thread):
        def __init__(self, socket, name):
            super().__init__()
            self.socket = socket
            self.name = name

        def run(self):
            while True:
                print('{}: '.format(self.name), end='')
                sys.stdout.flush()
                message = sys.stdin.readline()[:-1]
                if message[0:len("!send ")] == "!send ":
                    filename = message[len("!send "):]
                    filesize = os.path.getsize(filename)
                    SEPARATOR = "<SEPARATOR>"
                    # send the filename and filesize
                    self.socket.send(f"{filename}{SEPARATOR}{filesize}".encode())
                else:
                    self.socket.sendall(("TEXT" + ('{}: {}'.format(self.name, message))).encode())

    class Receiver(threading.Thread):
        def __init__(self, socket, name):
            super().__init__()
            self.socket = socket
            self.name = name
        
        def run(self):
            while True:
                message = self.socket.recv(1024).decode()
                if message:
                    print('\r{}\n{}: '.format(message, self.name), end = '')
                    # print("test")
                else:
                    print('\nLost connection to the server.')
                    self.socket.close()
                    os._exit(0)

    # serverName = '172.17.255.255'
    # serverName = '172.17.0.1'
    serverName = 'localhost' # Jed IP
    #serverName = '198.232.126.35' # Andrew IP
    # serverName = '172.17.255.255'
    serverPort = 12000

    # create TCP socket on client to use for connecting to remote server.  
    clientSocket = socket(AF_INET, SOCK_STREAM)

    # open the TCP connection
    clientSocket.connect((serverName,serverPort))

    username = input("Enter Username: ")
    print()

    sender = Sender(clientSocket, username)
    sender.start()

    receiver = Receiver(clientSocket, username)
    receiver.start()
