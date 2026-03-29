import socket
import threading
import sys
from colorama import init, Fore, Style

from crypto_utils import encrypt, decrypt

init(autoreset=True)

def receive_messages(client_socket):
    while True:
        try:
            encrypted = client_socket.recv(1024).decode('utf-8')
            if not encrypted:
                break
            message = decrypt(encrypted)
            if message.startswith("ERROR:"):
                print(f"\n{Fore.RED}{message}{Style.RESET_ALL}")
            elif message.startswith("REGISTER_OK"):
                print(f"\n{Fore.GREEN}Регистрация успешна! Можете писать сообщения.{Style.RESET_ALL}")
            else:
                # Обычное сообщение
                print(f"\n{Fore.CYAN}{message}{Style.RESET_ALL}")
            # После вывода снова показываем приглашение (если не выходим)
            print(f"{Fore.YELLOW}Вы: {Style.RESET_ALL}", end="", flush=True)
        except Exception as e:
            print(f"\n{Fore.RED}Ошибка соединения: {e}{Style.RESET_ALL}")
            break
    client_socket.close()
    print(f"{Fore.RED}Соединение разорвано.{Style.RESET_ALL}")
    sys.exit(0)

def start_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except Exception as e:
        print(f"{Fore.RED}Не удалось подключиться к серверу: {e}{Style.RESET_ALL}")
        return

    username = input(f"{Fore.YELLOW}Введите ваше имя: {Style.RESET_ALL}").strip()
    if not username:
        print(f"{Fore.RED}Имя не может быть пустым{Style.RESET_ALL}")
        return

    # Отправляем зашифрованную регистрацию
    client_socket.send(encrypt(f"REGISTER:{username}").encode('utf-8'))

    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    recv_thread.start()

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
