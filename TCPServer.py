from socket import *
from cryptography.fernet import Fernet # pip install cryptography
import threading
import sys
import os

answer = input("Will you host? ")

#example_key = 'MWwHhv8mDWBnuToB3uuV-5ISttlhzn1Dypb9KdiQOFI='

def encrypt(message, user_key):
    encoded_message = message.encode()
    cipher = Fernet(user_key)
    encrypted_message = cipher.encrypt(encoded_message)
    return encrypted_message

def decrypt(encrypted_message, user_key):
    cipher = Fernet(user_key)
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message.decode('utf-8')

def receiveFile(message, mySocket):
    SEPARATOR = "<SEPARATOR>"
    filename, filesize = message[4:].split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    with open(filename, "wb") as f:
        for _ in range(filesize):
            BUFFER_SIZE = 1
            # read bytes from the socket (receive)
            bytes_read = mySocket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)

def sendFile(filename, filesize, mySocket):
    with open(filename, "rb") as f:
        for _ in range(int(filesize)):
            # read the bytes from the file
            BUFFER_SIZE = 1 # send 4096 bytes each time step
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            mySocket.sendall(bytes_read)

if(answer == 'y'): # begin as server

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
                    print(message)
                    if message[:4] == "TEXT": 
                        for client in activeConnections:
                            if client != self: # send to every client except the one that sent this
                                client.socket.sendall(message.encode()) # send message after header
                    elif message[:4] == "FILE":
                        SEPARATOR = "<SEPARATOR>"
                        filename, filesize = message[4:].split(SEPARATOR)
                        receiveFile(message, self.socket)

                        # now send the file again
                        for client in activeConnections:
                            if client != self: # send to every client except the one that sent this
                                client.socket.sendall(("FILE" + f"{filename}{SEPARATOR}{filesize}{SEPARATOR}").encode()) 
                                sendFile(filename, filesize, client.socket)

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
                    self.socket.sendall(("FILE" + f"{filename}{SEPARATOR}{filesize}{SEPARATOR}").encode()) 
                    sendFile(filename, filesize, self.socket)
                else:
                    message = encrypt(message, user_key)  #comment this line to display wireshark functionality
                    self.socket.sendall(("TEXT" + ('{}: {}'.format(self.name, message))).encode())

    class Receiver(threading.Thread):
        def __init__(self, socket, name):
            super().__init__()
            self.socket = socket
            self.name = name
        
        def run(self):
            while True:
                message = self.socket.recv(1024).decode()
                if message[:4] == "TEXT": 
                    index = message.find("b'")
                    changed = message[index+2:].encode('utf-8')
                    try:
                        new_message = decrypt(changed, user_key)
                    except: # error is thrown here when encryption keys between users does not match
                        new_message = "ERROR: ENCRYPTION KEY IS DIFFERENT"
                    print('\r{}\n{}: '.format(message[4:index-1] + " " + new_message, self.name), end = '')
                elif message[:4] == "FILE":
                    print("Receiving File...")
                    # SEPARATOR = "<SEPARATOR>"
                    # filename, filesize = message[4:].split(SEPARATOR)
                    receiveFile(message, self.socket)

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
    user_key = input("Enter encryption key: ")
    print()

    sender = Sender(clientSocket, username)
    sender.start()

    receiver = Receiver(clientSocket, username)
    receiver.start()
