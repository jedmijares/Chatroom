from socket import *

serverPort = 12000

# create TCP welcoming socket
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(("",serverPort))

# server begins listening for incoming TCP requests
serverSocket.listen(1)

# output to console that server is listening
print ("The server is ready to receive... ")

while True:
    # server waits for incoming requests; new socket created on return
    connectionSocket, addr = serverSocket.accept()

    # read a sentence of bytes from socket sent by the client
    sentence = connectionSocket.recv(1024).decode()

    # output to console the sentence received from the client
    print ("Received From Client: ", sentence)
	
    # convert the sentence to upper case
    capitalizedSentence = sentence.upper()
	
    # send back modified sentence over the TCP connection
    connectionSocket.send(capitalizedSentence.encode())

    # output to console the sentence sent back to the client
    print ("Sent back to Client: ", capitalizedSentence)
	
    # close the TCP connection; the welcoming socket continues
    connectionSocket.close()
