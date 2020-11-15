from socket import *
import threading
import sys

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
                message = (self.socket.recv(1024)).decode('ascii')
                if message:
                    for client in activeConnections:
                        if client != self:
                            client.socket.sendall(message.encode('ascii'))

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

    #     # read a sentence of bytes from socket sent by the client
    #     sentence = connectionSocket.recv(1024).decode('ascii')

    #     # output to console the sentence received from the client
    #     print (sentence)

    #     # interactively get user's line to be converted to upper case
    #     capitalizedSentence = input("")
        
    #     # # convert the sentence to upper case
    #     # capitalizedSentence = sentence.upper()
        
    #     # send back modified sentence over the TCP connection
    #     connectionSocket.send((username + ': ' + capitalizedSentence).encode('ascii'))

    #     # output to console the sentence sent back to the client
    #     print (username + ':' + capitalizedSentence)
        
    #     # close the TCP connection; the welcoming socket continues
    # connectionSocket.close()
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
                self.socket.sendall('{}: {}'.format(self.name, message).encode('ascii'))

    class Receiver(threading.Thread):
        def __init__(self, socket, name):
            super().__init__()
            self.socket = socket
            self.name = name
        
        def run(self):
            while True:
                message = self.socket.recv(1024).decode('ascii')
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


    # while True:
    #     # interactively get user's line to be converted to upper case
    #     sentence = input("")

    #     # send the user's line over the TCP connection
    #     clientSocket.send((username + ': ' + sentence).encode('ascii'))

    #     #output to console what is sent to the server
    #     print (username + ': ' + sentence)

    #     # get user's line back from server having been modified by the server
    #     modifiedSentence = clientSocket.recv(1024).decode('ascii')

    #     # output the modified user's line
    #     print (modifiedSentence)

    # # close the TCP connection
    # clientSocket.close()
