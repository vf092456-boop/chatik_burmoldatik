import socket
import threading
from datetime import datetime
import sys

from crypto_utils import encrypt, decrypt
from storage import save_user, load_users, save_message

HOST = '0.0.0.0'
PORT = 12345

clients = []  # (socket, username)
users_lock = threading.Lock()

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def broadcast(message: str, sender_socket=None):
    encrypted_msg = encrypt(message)
    with users_lock:
        for sock, _ in clients:
            if sock != sender_socket:
                try:
                    sock.send(encrypted_msg.encode('utf-8'))
                except:
                    pass

def remove_client(client_socket):
    with users_lock:
        for i, (sock, name) in enumerate(clients):
            if sock == client_socket:
                username = name
                del clients[i]
                break
    broadcast(f"🔴 {username} покинул чат", sender_socket=client_socket)
    print(f"{Colors.YELLOW}{username} отключился{Colors.RESET}")

def handle_client(client_socket, addr):
    try:
        # 1. Получаем и расшифровываем регистрацию
        encrypted_data = client_socket.recv(1024).decode('utf-8')
        if not encrypted_data:
            client_socket.close()
            return
        try:
            data = decrypt(encrypted_data)
        except Exception as e:
            client_socket.send(encrypt("ERROR: Ошибка расшифровки").encode('utf-8'))
            client_socket.close()
            return

        if not data.startswith("REGISTER:"):
            client_socket.send(encrypt("ERROR: Неверный формат регистрации").encode('utf-8'))
            client_socket.close()
            return

        username = data.split(":", 1)[1].strip()
        if not username:
            client_socket.send(encrypt("ERROR: Имя не может быть пустым").encode('utf-8'))
            client_socket.close()
            return

        with users_lock:
            if any(name == username for _, name in clients):
                client_socket.send(encrypt("ERROR: Имя уже используется").encode('utf-8'))
                client_socket.close()
                return
            clients.append((client_socket, username))

        save_user(username)
        client_socket.send(encrypt("REGISTER_OK").encode('utf-8'))
        broadcast(f"🟢 {username} присоединился к чату", sender_socket=client_socket)
        print(f"{Colors.GREEN}{username} подключился {addr}{Colors.RESET}")

        # 2. Цикл приёма сообщений – каждое сообщение расшифровываем
        while True:
            encrypted_msg = client_socket.recv(1024).decode('utf-8')
            if not encrypted_msg:
                break
            try:
                plain_text = decrypt(encrypted_msg)
            except:
                continue

            if plain_text.startswith("/quit"):
                break

            full_message = f"{username}: {plain_text}"
            save_message(username, plain_text)
            broadcast(full_message, sender_socket=client_socket)
            print(f"{datetime.now().strftime('%H:%M:%S')} {full_message}")

    except Exception as e:
        print(f"Ошибка с клиентом {addr}: {e}")
    finally:
        remove_client(client_socket)
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Сервер запущен на {HOST}:{PORT}")
    print("Ожидание подключений...")

    while True:
        try:
            client_socket, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.daemon = True
            thread.start()
        except KeyboardInterrupt:
            print("\nСервер остановлен")
            break
        except Exception as e:
            print(f"Ошибка при принятии подключения: {e}")

if __name__ == "__main__":
    start_server()
