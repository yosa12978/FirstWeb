import socket
import signal
import sys
import asyncio

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5782

async def handle_connection(conn: socket):
    loop = asyncio.get_event_loop()

    req = (await loop.sock_recv(conn, 1024)).decode()

    http_request_header = req.split("\n")
    method, path, version = http_request_header[0].split(" ")
    print(f"Incoming request: {method} {path} {version}")

    file_name = path.removeprefix("/").split("?")[0]
    if file_name == "":
        file_name = "index.html"

    file_path = f"assets/{file_name}"
    try:
        f = open(file_path, "r")
    except:
        f = open("assets/not_found.html", "r")

    html_page = f.read()
    
    resp = f'HTTP/1.0 200 OK\n\n{html_page}'
    await loop.sock_sendall(conn, resp.encode())
    conn.close()

async def web_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER_HOST, SERVER_PORT))
    sock.listen()
    sock.setblocking(False)

    loop = asyncio.get_event_loop()
    print(f"Listening on port {SERVER_PORT}")
    while True:
        conn, _ = await loop.sock_accept(sock)
        loop.create_task(handle_connection(conn))

def interrupt_handler(sig, frame):
    print('\nHalting Web Server...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, interrupt_handler)
    asyncio.run(web_server())
    signal.pause()
