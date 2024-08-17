import socket
import time
import argparse
import os
import sys

# Constants
BUFFER_SIZE = 8192  # 8 KB buffer
DEFAULT_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
DEFAULT_PORT = 12345


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"


def generate_test_file(size):
    filename = "test_file.bin"
    with open(filename, "wb") as f:
        f.write(os.urandom(size))
    return filename


def run_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)

    local_ip = get_local_ip()
    print(f"Server listening on {local_ip}:{port}")
    print(f"Run the client using: python {sys.argv[0]} --client {local_ip}")

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address}")

        filename = generate_test_file(DEFAULT_FILE_SIZE)
        file_size = os.path.getsize(filename)

        with open(filename, 'rb') as f:
            client_socket.send(str(file_size).encode())

            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                client_socket.send(data)

        client_socket.close()
        os.remove(filename)
        print("Test completed. Waiting for next client...")


def run_client(server_ip, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, port))
    except socket.gaierror:
        print(f"Error: Unable to connect to {server_ip}. Please check the IP address and ensure the server is running.")
        sys.exit(1)
    except ConnectionRefusedError:
        print(f"Error: Connection refused. Please ensure the server is running on {server_ip}:{port}")
        sys.exit(1)

    try:
        file_size = int(client_socket.recv(BUFFER_SIZE).decode())
        print(f"Receiving file of size: {file_size / (1024 * 1024):.2f} MB")

        received_data = 0
        start_time = time.time()

        while received_data < file_size:
            data = client_socket.recv(BUFFER_SIZE)
            received_data += len(data)

            progress = (received_data / file_size) * 100
            print(f"Progress: {progress:.2f}%", end='\r')

        end_time = time.time()
        duration = end_time - start_time
        speed = (file_size / duration) / (1024 * 1024)  # MB/s

        print(f"\nTransfer completed in {duration:.2f} seconds")
        print(f"Average speed: {speed:.2f} MB/s")
    finally:
        client_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LAN Speed Test")
    parser.add_argument("--server", action="store_true", help="Run as server")
    parser.add_argument("--client", help="Run as client and connect to server IP")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to use")

    args = parser.parse_args()

    if args.server:
        run_server(args.port)
    elif args.client:
        run_client(args.client, args.port)
    else:
        print("Please specify either --server or --client")
        print(f"Example server: python {sys.argv[0]} --server")
        print(f"Example client: python {sys.argv[0]} --client SERVER_IP")