import threading
import socket
from datetime import datetime

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()

def get_current_time():
    """Returns the current time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def handle_client(conn, addr):
    try:
        username = conn.recv(1024).decode(FORMAT)
        print(f"[{get_current_time()}] {addr} connected as {username}.")
        
        with clients_lock:
            clients[username] = conn

        join_message = f"{username} joined the chat!"
        broadcast_message(join_message, conn)

        # Send list of active users to the new client
        send_user_list(conn)

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                disconnect_message = f"{username} has left the chat."
                print(disconnect_message)
                broadcast_message(disconnect_message, conn)
            elif msg.startswith('@'):
                target_usr_name = msg.split('@')[1].split()[0]
                private_message(username, target_usr_name, msg)
            else:
                formatted_message = f"[{get_current_time()}] {username}: {msg}"
                print(formatted_message)
                broadcast_message(formatted_message, conn)

    finally:
        with clients_lock:
            del clients[username]
        conn.close()

def broadcast_message(message, sender_conn=None):
    """Broadcasts a message to all clients except the sender."""
    with clients_lock:
        for client in clients.values():
            if client != sender_conn:
                try:
                    client.sendall(message.encode(FORMAT))
                except Exception as e:
                    print(f"[ERROR] Failed to send message: {e}")

def send_user_list(conn):
    """Sends the list of connected users to the given connection."""
    user_list = "Active users: " + ", ".join(clients.keys())
    conn.sendall(user_list.encode(FORMAT))

def private_message(sender, target_username, msg):
    """Sends a private message to the target user."""
    with clients_lock:
        if target_username in clients:
            private_msg = f"[PRIVATE] {sender} to {target_username}: {msg}"
            target_conn = clients[target_username]
            try:
                target_conn.sendall(private_msg.encode(FORMAT))
                print(f"[PRIVATE] {sender} to {target_username}: {msg}")
            except Exception as e:
                print(f"[ERROR] Could not send private message: {e}")
        else:
            error_msg = f"User @{target_username} not found!"
            clients[sender].sendall(error_msg.encode(FORMAT))

def server_input():
    """Enables server admins to send broadcast messages."""
    while True:
        message = input("[Server]: ")
        if message:
            broadcast_message(f"[Server]: {message}")

def start():
    print('[SERVER STARTED]')
    server.listen()

    threading.Thread(target=server_input, daemon=True).start()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()
