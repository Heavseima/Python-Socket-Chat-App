import socket
import threading
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
    """Connect to the server."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[{get_current_time()}] Connected to the server.")
    return client

def receive_messages(client):
    """Continuously receive and print messages from the server."""
    while True:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if msg:
                print(f"\r[{get_current_time()}] {msg}\n", end="", flush=True)
        except Exception as e:
            print(f"[ERROR] Connection closed or failed: {e}")
            break

def start():
    """Start the message listener."""
    connection = connect()

    # Start a thread to handle incoming messages
    receive_thread = threading.Thread(target=receive_messages, args=(connection,))
    receive_thread.daemon = True
    receive_thread.start()

    # Keep the program running to continue receiving messages
    receive_thread.join()

start()
