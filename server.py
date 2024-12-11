import socket
from multiprocessing import Process
import pyodbc as pbc


def handle_client(conn, addr, buffer):
    print('Connected by', addr)
    with conn:
        while True:
            data = conn.recv(buffer)
            if not data or data.decode() == 'exit':
                print(f"Connection closed by {addr}")
                break
            print(f"Received: {data.decode()}")
            conn.sendall(data)  # Echo the received message back to the client


def get_contacts(db_cursor, user_id):
    """获取user_id用户的所有联系人姓名"""
    sql_query = """
        SELECT
            CASE
                WHEN F.User1ID = ? THEN U2.Username
                ELSE U1.Username
            END AS FriendName
        FROM
            Friendships F
        JOIN
            Users U1 ON F.User1ID = U1.UserID
        JOIN
            Users U2 ON F.User2ID = U2.UserID
        WHERE
            (F.User1ID = ? OR F.User2ID = ?)
            AND F.Status = 'Accepted';
    """
    db_cursor.execute(sql_query, (user_id, user_id, user_id))
    rows = db_cursor.fetchall()
    if len(rows) == 0:
        return None
    else:
        return '\n'.join(rows)


def start_server(host='127.0.0.1', port=65432, buffer=1024):
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
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"  # 例如 'localhost' 或 IP 地址
        "DATABASE=InstantMessagingDB;"
        "Trusted_Connection=yes;"
    )
    with pbc.connect(conn_str) as conn:
        print("数据库连接成功")
        with conn.cursor() as cursor:
            server_ip_addr = '127.0.0.1'
            server_port = 65432
            buffer_size = 1024
            start_server(server_ip_addr, server_port, buffer_size)