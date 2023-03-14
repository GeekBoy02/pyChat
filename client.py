import socket
import threading

HOST = input("Enter server IPv6 address: ")
PORT = 10000

# Create a socket object
client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((HOST, PORT))

# Get the client username
username = input("Enter a username: ")
client_socket.sendall(username.encode())

def receive_messages():
    """Receives messages from the server and prints them to the console"""
    while True:
        message = client_socket.recv(1024).decode()
        print(message)

# Start a thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

while True:
    # Get user input and send it to the server
    message = input("")
    client_socket.sendall(message.encode())
