import socket
from multiprocessing import Process

def handle_client(conn, addr):
    print('Connected by', addr)
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode()}")
            conn.sendall(data)

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            # 每个新连接启动一个新进程
            Process(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    server_ip_addr = '127.0.0.1'
    port = 65432
    start_server(server_ip_addr, port)