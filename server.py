import socket
from multiprocessing import Process
import pyodbc as pbc

from server_utils import *


def handle_client(conn, addr, buffer):
    print('Connected by', addr)
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"  # 例如 'localhost' 或 IP 地址
        "DATABASE=InstantMessagingDB;"
        "Trusted_Connection=yes;"
    )
    with pbc.connect(conn_str) as db_conn:
        print("数据库连接成功")
        with db_conn.cursor() as db_cursor:
            with conn:
                while True:
                    data = conn.recv(buffer)
                    if not data or data.decode() == 'exit':
                        print(f"Connection closed by {addr}")
                        break
                    data = data.decode().split('\n')
                    cmd, user_id = int(data[0]), data[1]
                    print(f"Received: {data}")
                    send_msg = give_data(cmd, db_conn, db_cursor, user_id, data)
                    conn.sendall(send_msg.encode())


def start_server(host, port, buffer):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        with s:
            while True:
                conn, addr = s.accept()
                # 每个新连接启动一个新进程
                Process(target=handle_client, args=(conn, addr, buffer)).start()


if __name__ == "__main__":
    server_ip_addr = '10.150.220.87'
    server_port = 65432
    buffer_size = 1024
    start_server(server_ip_addr, server_port, buffer_size)
