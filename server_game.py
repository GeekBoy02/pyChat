import socket
import threading
import json
import os
import random

HOST = '::'  # Listen on all available IPv6 interfaces
PORT = 10000

# List to keep track of connected clients
clients = []

# Create a socket object
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Bind the socket to a public host and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()

# Load or create the data file
if os.path.exists("user_data.json"):
    with open("user_data.json", "r") as f:
        user_data = json.load(f)
else:
    user_data = {}


def save_user_data():
    """Saves the user data to a file"""
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)


def handle_client(client_socket, client_address):
    """Handles a client connection"""
    # Get the client username
    username = client_socket.recv(1024).decode()
    print(f"New connection from {client_address} with username {username}")

    # Add the client to the list of connected clients
    clients.append((username, client_socket))

    # Get the user data or create it if it doesn't exist
    if username not in user_data:
        user_data[username] = {"messages_sent": 0, "times_connected": 1, "class": "Soldier",
                               "level": 1, "xp": 0, "health": 100, "speed": 15, "intellect": 7, "luck": 10, "freeAP": 1}
        save_user_data()

    while True:
        try:
            # Receive a message from the client
            message = client_socket.recv(1024).decode()
            if not message:
                # If an empty message is received, the client has disconnected
                raise Exception()

            if message.startswith("!class "):
                # Set the user's class
                user_class = message.split()[1].title()
                if user_class in ["Soldier", "Engineer", "Explorer"]:
                    user_data[username]["class"] = user_class
                    save_user_data()
                    client_socket.sendall(
                        f"You are now a {user_class}!".encode())
                else:
                    client_socket.sendall(
                        "Invalid class. Valid classes are Warrior, Mage, and Rogue.".encode())

            elif message.startswith("!f ") or message.startswith("!fight "):
                enemy_lvl = message.split()[1].title()
                if enemy_lvl.isdigit() and int(enemy_lvl) > 0:
                    # Fight an Enemy
                    player = Player(username, user_data[username]["class"], user_data[username]["level"], user_data[username]["health"], user_data[username]
                                    ["speed"], user_data[username]["intellect"], user_data[username]["luck"], user_data[username]["xp"], user_data[username]["freeAP"], client_socket)
                    enemy = Enemy(int(enemy_lvl))

                    if battle(player, enemy):
                        print(f"{username} wins against {enemy.name}")
                    else:
                        client_socket.sendall(
                            f"{username} lost the battle".encode())
                else:
                    client_socket.sendall(
                        f"Input a valid Enemy Level you want to fight against, for example with: !fight 4, you will fight against a level 4 Enemy".encode())

            elif message.startswith("!d ") or message.startswith("!duel "):
                enemy_player = message.split()[1].title()
                if is_user_connected(enemy_player):
                    # Fight another Player if he/she is online
                    player = Player(username, user_data[username]["class"], user_data[username]["level"], user_data[username]["health"], user_data[username]
                                    ["speed"], user_data[username]["intellect"], user_data[username]["luck"], user_data[username]["xp"], user_data[username]["freeAP"], client_socket)
                    enemy = Player(enemy_player, user_data[enemy_player]["class"], user_data[enemy_player]["level"], user_data[enemy_player]["health"], user_data[enemy_player]
                                   ["speed"], user_data[enemy_player]["intellect"], user_data[enemy_player]["luck"], user_data[enemy_player]["xp"], user_data[enemy_player]["freeAP"], client_socket)
                    player.fight(enemy)
                    
                else:
                    client_socket.sendall(
                        f"Input a Opponent you want to fight against, the User needs to be connected to the server".encode())

            elif message.startswith("!aa ") or message.startswith("!allocate attributes "):
                # allocate attributes
                speed = message.split()[1]
                intellect = message.split()[2]
                luck = message.split()[3]
                if speed.isdigit() and int(speed) > 0 or intellect.isdigit() and int(intellect) > 0 or luck.isdigit() and int(luck) > 0:
                    player = Player(username, user_data[username]["class"], user_data[username]["level"], user_data[username]["health"], user_data[username]
                                    ["speed"], user_data[username]["intellect"], user_data[username]["luck"], user_data[username]["xp"], user_data[username]["freeAP"], client_socket)
                    player.allocate_attributes(
                        int(speed), int(intellect), int(luck))
                else:
                    client_socket.sendall(
                        f"Input a valid number of free AP you want to use, for example with: !aa 4 2 1, you will increase speed by 4, intellect by 2, and luck by 1".encode())

            elif message == "!a" or message == "!attributes":
                # show attributes
                player = Player(username, user_data[username]["class"], user_data[username]["level"], user_data[username]["health"], user_data[username]
                                ["speed"], user_data[username]["intellect"], user_data[username]["luck"], user_data[username]["xp"], user_data[username]["freeAP"], client_socket)
                player.get_attributes()

            elif message == "!h" or message == "!help":
                # show help
                help_command(client_socket)

            elif message == "!users":
                # Send a list of connected users to the client
                user_list = "Connected users:\n" + \
                    "\n".join([u[0] for u in clients])
                client_socket.sendall(user_list.encode())

            else:
                # Send the message to all connected clients
                for user, sock in clients:
                    sock.sendall(f"{username}: {message}".encode())

                # Increment the user's message count, XP, and level
                user_data[username]["messages_sent"] += 1
                save_user_data()

        except:
            # Remove the client from the list of connected clients
            clients.remove((username, client_socket))
            print(f"Connection closed with {client_address}")
            client_socket.close()
            break


print(f"Server listening on [{HOST}]:{PORT}")

# payer and enemy classes


class Player:
    def __init__(self, name, player_class, level, health, speed, intellect, luck, xp, freeAP, client_socket):
        self.name = name
        self.player_class = player_class
        self.level = level
        self.health = 100 + self.level * 20
        self.speed = speed
        self.intellect = intellect
        self.luck = luck
        self.xp = xp
        self.freeAP = freeAP
        self.client_socket = client_socket

    def level_up(self):
        playedDidLvlUp = False
        while self.xp >= (self.level * 100):
            self.level += 1
            self.freeAP += 5
            playedDidLvlUp = True
            # stat_increase = random.choice(["speed", "intellect", "luck"])
            # setattr(self, stat_increase, getattr(self, stat_increase) + 5)
            self.client_socket.send(
                f"{self.name} leveled up to level {self.level} and increased their freeAP by 5!".encode())
            user_data[self.name]["level"] = self.level
            user_data[self.name]["freeAP"] = self.freeAP
            # self.health = 100 + self.level * 20
            # user_data[self.name]["health"] = self.health
            # user_data[self.name]["speed"] = self.speed
            # user_data[self.name]["intellect"] = self.intellect
            # user_data[self.name]["luck"] = self.luck
            save_user_data()
        if playedDidLvlUp:
            self.xp = 0
            user_data[self.name]["xp"] = self.xp
            playedDidLvlUp = False

    def attack_enemy(self, enemy):
        damage = (self.speed * random.uniform(0.8, 1.2)) - \
            (enemy.intellect * random.uniform(0.8, 1.2))
        critical_hit_chance = min(0.3 + (self.luck / 100), 0.6)
        if random.random() < critical_hit_chance:
            damage *= 2
        enemy.health -= max(damage, 0)
        self.client_socket.sendall(
            f"{self.name} hits {enemy.name} for {int(damage)} \n".encode())

        if enemy.health <= 0:
            self.client_socket.sendall(
                f"{self.name} defeated {enemy.name} with {int(self.health)} HP remaining!".encode())
            xp = enemy.level * 10
            self.xp += xp
            user_data[self.name]["xp"] = self.xp
            save_user_data()
            self.client_socket.sendall(
                f"{self.name} gained {xp} XP!".encode())
            self.level_up()

    def fight(self, enemy):
        # Choose who attacks first based on speed
        if self.speed >= enemy.speed:
            attacker = self
            defender = enemy
        else:
            attacker = enemy
            defender = self

        while True:
            # Attacker attacks the defender
            attacker.attack_enemy(defender)
            if defender.health <= 0:
                # Defender has been defeated
                self.client_socket.sendall(
                    f"{defender.name} has been defeated!".encode())
                break

            # Switch roles for next round
            attacker, defender = defender, attacker

    def allocate_attributes(self, speed_points, intellect_points, luck_points):
        if (speed_points + intellect_points + luck_points) > self.freeAP:
            self.client_socket.sendall(
                f"Insufficient free attribute points.".encode())
            return

        self.speed += speed_points
        self.intellect += intellect_points
        self.luck += luck_points
        self.freeAP -= speed_points + intellect_points + luck_points
        user_data[self.name]["speed"] = self.speed
        user_data[self.name]["intellect"] = self.intellect
        user_data[self.name]["luck"] = self.luck
        user_data[self.name]["freeAP"] = self.freeAP
        save_user_data()
        self.client_socket.sendall(
            f"{self.name} allocated {speed_points} points to speed, {intellect_points} points to intellect, and {luck_points} points to luck.".encode())

    def get_attributes(self):
        attributes = f"Name: {self.name}\n"
        attributes += f"Class: {self.player_class}\n"
        attributes += f"Level: {self.level}\n"
        attributes += f"Experience: {self.xp}\n"
        attributes += f"Health: {self.health}\n"
        attributes += f"Speed: {self.speed}\n"
        attributes += f"Intellect: {self.intellect}\n"
        attributes += f"Luck: {self.luck}\n"
        attributes += f"Free Attribute Points: {self.freeAP}\n"
        self.client_socket.sendall(attributes.encode())


class Enemy:
    def __init__(self, level):
        self.name = "Rouge Drone"
        self.level = level
        self.health = (50 + (level * 10)) * random.uniform(0.8, 1.2)
        self.speed = (5 + (level * 2)) * random.uniform(0.8, 1.2)
        self.intellect = (5 + (level*2)) * random.uniform(0.8, 1.2)
        self.luck = (5 + (level*2))*random.uniform(0.8, 1.2)

    def attack_player(self, player):
        damage = (self.speed*random.uniform(0.8, 1.2)) - \
            player.intellect*random.uniform(0.8, 1.2)
        critical_hit_chance = min((0+3+self.luck/100), 6)
        if random.random() < critical_hit_chance:
            damage *= 2
        player.health -= max(damage, 0)
        player.client_socket.sendall(
            f"{self.name} hits {player.name} for {int(damage)}\n".encode())


def battle(player: Player, enemy: Enemy) -> bool:
    while True:
        player.attack_enemy(enemy)
        if enemy.health <= 0:
            return True
        enemy.attack_player(player)
        if player.health <= 0:
            return False


def help_command(client_socket):
    """Sends information about the available commands to the client"""
    help_message = """
    Available commands:
    !class [class_name] - Sets the user's class to [class_name], which must be one of: Soldier, Engineer, Explorer
    !fight [enemy_level] - Initiates a battle with an enemy of the specified level
    !duel [username] - Initiates a battle with another User if he/she is online
    !allocate attributes [speed] [intellect] [luck] - Increases the user's speed, intellect, and luck attributes by the specified amounts
    !attributes - Displays the user's current attributes
    !users - Displays a list of all connected users
    """
    client_socket.sendall(help_message.encode())


def is_user_connected(username):
    for client in clients:
        if client[0] == username:
            return True
    return False


while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()

    # Create a new thread to handle the client connection
    thread = threading.Thread(target=handle_client,
                              args=(client_socket, client_address))
    thread.start()
