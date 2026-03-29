import socket
import threading

# Настройки сервера
HOST = '127.0.0.1'  # локальный хост (для тестирования)
PORT = 12345        # порт для прослушивания

# Список активных клиентов (сокетов)
clients = []
# Защита списка от одновременного доступа из разных потоков
lock = threading.Lock()

def broadcast(message, sender_socket=None):
    """Отправляет сообщение всем клиентам, кроме отправителя (если указан)."""
    with lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    # Если не удалось отправить, клиент, вероятно, отключился
                    client.close()
                    if client in clients:
                        clients.remove(client)

def handle_client(client_socket, address):
    """Обрабатывает сообщения от одного клиента."""
    print(f"Подключён {address}")
    try:
        while True:
            # Принимаем сообщение (до 1024 байт)
            message = client_socket.recv(1024)
            if not message:
                break  # клиент закрыл соединение
            # Рассылаем всем остальным
            broadcast(message, sender_socket=client_socket)
    except:
        pass
    finally:
        # Удаляем клиента из списка и закрываем сокет
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        print(f"Отключён {address}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Сервер запущен на {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        with lock:
            clients.append(client_socket)
        # Запускаем поток для обработки нового клиента
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()