from server.server import start_server
import sys


if __name__ == "__main__":
    # Usa el primer argumento como IP si se pasa, si no, usa 127.0.0.1
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = 65431
    start_server(host, port)