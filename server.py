import os
import sys
import signal
from concurrent.futures import ThreadPoolExecutor
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import socket
import argparse

# Set the port number
DEFAULT_PORT = 8000

# Set the maximum number of concurrent connections
MAX_WORKERS = 10


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    allow_reuse_address = True


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's public DNS server
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"  # Localhost if unable to determine IP


def signal_handler(sig, frame):
    print("\nShutting down the server...")
    sys.exit(0)


def run_server(port, directory):
    os.chdir(directory)
    handler = SimpleHTTPRequestHandler
    with ThreadedHTTPServer(("", port), handler) as httpd:
        local_ip = get_local_ip()
        print(f"Server started at port {port}")
        print(f"Sharing folder: {os.path.abspath(directory)}")
        print(f"Access the shared folder at:")
        print(f"  Local access: http://localhost:{port}")
        print(f"  Network access: http://{local_ip}:{port}")
        print("Press Ctrl+C to stop the server.")

        # Set up the signal handler
        signal.signal(signal.SIGINT, signal_handler)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()
            print("\nServer stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Share a directory over HTTP")
    parser.add_argument("-d", "--directory", default=os.getcwd(),
                        help="Directory to share (default: current directory)")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT, help=f"Port to use (default: {DEFAULT_PORT})")
    args = parser.parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    print(f"Sharing directory: {directory}")

    run_server(args.port, directory)