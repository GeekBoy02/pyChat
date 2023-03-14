import socket
import threading

HOST = '::' # Listen on all available IPv6 interfaces
PORT = 55555

# List to keep track of connected clients
clients = []

# Create a socket object
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Bind the socket to a public host and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()

def handle_client(client_socket, client_address):
    """Handles a client connection"""
    # Get the client username
    username = client_socket.recv(1024).decode()
    print(f"New connection from {client_address} with username {username}")

    # Add the client to the list of connected clients
    clients.append((username, client_socket))

    while True:
        try:
            # Receive a message from the client
            message = client_socket.recv(1024).decode()
            if not message:
                # If an empty message is received, the client has disconnected
                raise Exception()

            if message == "!users":
                # Send a list of connected users to the client
                user_list = "Connected users:\n" + "\n".join([u[0] for u in clients])
                client_socket.sendall(user_list.encode())
            else:
                # Send the message to all connected clients (except the sender)
                for user, sock in clients:
                    sock.sendall(f"{username}: {message}".encode())
        except:
            # Remove the client from the list of connected clients
            clients.remove((username, client_socket))
            print(f"Connection closed with {client_address}")
            client_socket.close()
            break

print(f"Server listening on [{HOST}]:{PORT}")

while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()

    # Create a new thread to handle the client connection
    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()
