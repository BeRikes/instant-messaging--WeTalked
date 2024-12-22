import multiprocessing
import socket
from multiprocessing import Process
import pyodbc as pbc
from server_utils import *


def handle_client(conn, addr, buffer, username2addr):
    print('Connected by', addr)
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"  # 例如 'localhost' 或 IP 地址
        "DATABASE=InstantMessagingDB;"
        "Trusted_Connection=yes;"
    )
    user_name = ''
    with pbc.connect(conn_str) as db_conn:
        print("数据库连接成功")
        with db_conn.cursor() as db_cursor:
            with conn:
                while True:
                    data = conn.recv(10 * buffer)
                    if not data:
                        print(f"Connection closed by {addr}")
                        break
                    data = data.decode().split('\n')
                    print(f"Received: {data}")
                    cmd, u_name = int(data[0]), data[1]
                    if cmd == 0:
                        user_name = u_name     # 保护用户数据安全
                        username2addr[user_name] = addr
                        print(username2addr)
                    elif cmd == 1:
                        user_name = u_name
                    send_msg = give_data(cmd, db_conn, db_cursor, user_name, data, username2addr)
                    conn.sendall(send_msg.encode())


def start_server(host, port, buffer, username2addr):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        with s:
            while True:
                conn, addr = s.accept()
                # 每个新连接启动一个新进程
                Process(target=handle_client, args=(conn, addr, buffer, username2addr)).start()


if __name__ == "__main__":
    server_ip_addr = '10.150.220.87'
    server_port = 65432
    buffer_size = 40960
    with multiprocessing.Manager() as manager:
        username2addr = manager.dict()    # 子进程之间共享的数据
        start_server(server_ip_addr, server_port, buffer_size, username2addr)
