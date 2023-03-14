import socket
import threading
import sys
import curses

# Initialize ncurses
stdscr = curses.initscr()

# Get terminal dimensions
term_height, term_width = stdscr.getmaxyx()

# Create text input box
input_box = curses.newwin(1, term_width - 2, term_height - 1, 1)
input_box.addstr(0, 0, "> ")
input_box.refresh()

# Create message display box
message_box = curses.newwin(term_height - 2, term_width - 2, 0, 1)
message_box.scrollok(True)
message_box.idlok(True)
message_box.refresh()

# Create socket object
server_address = ('::1', 55555)  # Use IPv6 address and port
client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Function to receive messages from the server
def receive():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            message_box.addstr(message + '\n')
            message_box.refresh()
        except:
            # Handle any errors that occur during message reception
            print("An error occurred while receiving messages.")
            client_socket.close()
            sys.exit()

# Function to send messages to the server
def send():
    while True:
        message = input_box.getstr().decode('utf-8')
        if message == "!quit":
            client_socket.close()
            sys.exit()
        else:
            try:
                client_socket.sendall(message.encode('utf-8'))
                input_box.clear()
                input_box.addstr(0, 0, "> ")
                input_box.refresh()
            except:
                # Handle any errors that occur during message sending
                print("An error occurred while sending messages.")
                client_socket.close()
                sys.exit()

# Function to get user's name
def get_username():
    input_box.addstr(0, 0, "Enter your name: ")
    username = input_box.getstr().decode('utf-8')
    input_box.clear()
    input_box.addstr(0, 0, "> ")
    input_box.refresh()
    return username

# Connect to server
client_socket.connect(server_address)

# Get user's name and send it to server
username = get_username()
client_socket.sendall(username.encode('utf-8'))

# Start message receive and send threads
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()

# Wait for threads to finish
receive_thread.join()
send_thread.join()

# Clean up ncurses before exiting
curses.endwin()
