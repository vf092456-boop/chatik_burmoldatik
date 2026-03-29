import socket
import threading
import sys

# Настройки подключения
HOST = '127.0.0.1'  # IP сервера (при запуске на разных машинах укажите реальный IP)
PORT = 12345

def receive_messages(client_socket):
    """Постоянно получает сообщения от сервера и выводит их на экран."""
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"\n{message}")  # вывод сообщения с новой строки
            # После вывода снова выводим приглашение для ввода (необязательно)
            print("Вы: ", end="", flush=True)
    except:
        pass
    finally:
        print("Соединение с сервером потеряно.")
        client_socket.close()
        sys.exit(0)

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except:
        print("Не удалось подключиться к серверу.")
        return

    print("Подключено к чату. Введите /quit для выхода.")

    # Запускаем поток для приёма сообщений
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receive_thread.start()

    # Основной цикл для отправки сообщений
    try:
        while True:
            message = input("Вы: ")
            if message.lower() == "/quit":
                break
            # Отправляем сообщение, добавляя метку имени (для простоты имя не запрашиваем)
            # Можно добавить имя пользователя, но в данном примере сообщения просто пересылаются как есть
            client_socket.send(message.encode('utf-8'))
    except:
        pass
    finally:
        client_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    start_client()