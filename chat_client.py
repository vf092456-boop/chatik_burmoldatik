import socket
import threading
import sys
from colorama import init, Fore, Style
import getpass

from crypto_utils import encrypt, decrypt

# Инициализация colorama для Windows
init(autoreset=True)

def receive_messages(client_socket):
    """Поток приёма сообщений"""
    while True:
        try:
            encrypted = client_socket.recv(1024).decode('utf-8')
            if not encrypted:
                break
            message = decrypt(encrypted)
            # Форматируем вывод: если сообщение системное, оно уже содержит эмодзи или начинается с /
            if message.startswith("ERROR:"):
                print(f"{Fore.RED}{message}{Style.RESET_ALL}")
            elif message.startswith("REGISTER_OK"):
                print(f"{Fore.GREEN}Регистрация успешна! Можете писать сообщения.{Style.RESET_ALL}")
            else:
                # Обычное сообщение: выводим с новой строки
                print(f"\r{Fore.CYAN}{message}{Style.RESET_ALL}")
                # Возвращаем приглашение на новой строке
                print(f"{Fore.YELLOW}Вы: {Style.RESET_ALL}", end="", flush=True)
        except Exception as e:
            print(f"\n{Fore.RED}Ошибка соединения: {e}{Style.RESET_ALL}")
            break
    # При выходе из цикла закрываем сокет
    client_socket.close()
    print(f"{Fore.RED}Соединение разорвано.{Style.RESET_ALL}")
    sys.exit(0)

def start_client(host, port):
    client_socket = socket.socket(socket.AF_INTERNET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except Exception as e:
        print(f"{Fore.RED}Не удалось подключиться к серверу: {e}{Style.RESET_ALL}")
        return

    # Запрашиваем имя пользователя
    username = input(f"{Fore.YELLOW}Введите ваше имя: {Style.RESET_ALL}").strip()
    if not username:
        print(f"{Fore.RED}Имя не может быть пустым{Style.RESET_ALL}")
        return

    # Отправляем регистрацию
    client_socket.send(encrypt(f"REGISTER:{username}").encode('utf-8'))

    # Запускаем поток приёма
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    recv_thread.start()

    # Основной цикл отправки
    print(f"{Fore.GREEN}Подключено к чату. Введите /quit для выхода.{Style.RESET_ALL}")
    try:
        while True:
            msg = input(f"{Fore.YELLOW}Вы: {Style.RESET_ALL}")
            if msg.lower() == "/quit":
                client_socket.send(encrypt("/quit").encode('utf-8'))
                break
            if msg:
                client_socket.send(encrypt(msg).encode('utf-8'))
    except KeyboardInterrupt:
        pass
    finally:
        client_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Использование: python client.py <хост> <порт>")
        print(f"Пример: python client.py 5.tcp.eu.ngrok.io 13775")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    start_client(host, port)
