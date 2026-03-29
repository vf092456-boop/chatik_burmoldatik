import socket
import threading
from datetime import datetime
import sys

from crypto_utils import encrypt, decrypt
from storage import save_user, load_users, save_message

HOST = '0.0.0.0'          # Слушаем все интерфейсы (для ngrok)
PORT = 12345              # Порт, который будет пробрасывать ngrok

# Глобальные структуры
clients = []              # Список (socket, username)
users_lock = threading.Lock()

# Цвета для консоли сервера (опционально)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def broadcast(message: str, sender_socket=None):
    """Отправляет сообщение всем клиентам, кроме отправителя"""
    encrypted_msg = encrypt(message)
    with users_lock:
        for sock, _ in clients:
            if sock != sender_socket:
                try:
                    sock.send(encrypted_msg.encode('utf-8'))
                except:
                    # Если клиент отвалился, удалим его позже
                    pass

def remove_client(client_socket):
    """Удаляет клиента из списка и закрывает сокет"""
    with users_lock:
        for i, (sock, name) in enumerate(clients):
            if sock == client_socket:
                username = name
                del clients[i]
                break
    # Уведомляем остальных о выходе
    broadcast(f"🔴 {username} покинул чат", sender_socket=client_socket)
    print(f"{Colors.YELLOW}{username} отключился{Colors.RESET}")

def handle_client(client_socket, addr):
    """Обрабатывает одного клиента"""
    # Ожидаем регистрацию
    try:
        # Первое сообщение должно быть вида "REGISTER:имя"
        data = client_socket.recv(1024).decode('utf-8')
        if not data.startswith("REGISTER:"):
            client_socket.close()
            return
        username = data.split(":", 1)[1].strip()
        if not username:
            client_socket.send(encrypt("ERROR: Имя не может быть пустым").encode('utf-8'))
            client_socket.close()
            return

        # Проверяем, занято ли имя
        with users_lock:
            if any(name == username for _, name in clients):
                client_socket.send(encrypt("ERROR: Имя уже используется").encode('utf-8'))
                client_socket.close()
                return
            # Добавляем в активные
            clients.append((client_socket, username))

        # Сохраняем пользователя в файл (если новый)
        save_user(username)

        # Подтверждение регистрации
        client_socket.send(encrypt("REGISTER_OK").encode('utf-8'))

        # Оповещаем остальных
        broadcast(f"🟢 {username} присоединился к чату", sender_socket=client_socket)
        print(f"{Colors.GREEN}{username} подключился {addr}{Colors.RESET}")

        # Основной цикл приёма сообщений
        while True:
            encrypted_msg = client_socket.recv(1024).decode('utf-8')
            if not encrypted_msg:
                break
            # Расшифровываем
            try:
                plain_text = decrypt(encrypted_msg)
                if plain_text.startswith("/quit"):
                    break
                # Формируем сообщение с ником
                full_message = f"{username}: {plain_text}"
                # Сохраняем в историю
                save_message(username, plain_text)
                # Рассылаем всем остальным
                broadcast(full_message, sender_socket=client_socket)
                # Выводим на сервер для лога
                print(f"{datetime.now().strftime('%H:%M:%S')} {full_message}")
            except Exception as e:
                print(f"Ошибка обработки сообщения от {username}: {e}")
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
