import socket
import threading
import time
from datetime import datetime

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

def get_current_time():
    """Returns the current time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    return client

def send(client, msg):
    try:
        message = msg.encode(FORMAT)
        client.sendall(message)
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

def receive(client):
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message:
                print(f"\r{message}\n{username}: ", end="", flush=True)
        except Exception as e:
            print(f"[ERROR] {e}")
            break

def start():
    global username
    username = input('Enter your username: ')
    answer = input(f'Connect with username: {username} (yes/no)? ')
    if answer.lower() != 'yes':
        return

    connection = connect()
    send(connection, username)

    receive_thread = threading.Thread(target=receive, args=(connection,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        msg = input(f"{username}: ")
        if msg.lower() == 'q':
            send(connection, DISCONNECT_MESSAGE)
            break
        send(connection, msg)

    print('Disconnected')
    connection.close()

start()
