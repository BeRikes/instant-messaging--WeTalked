import socket
from multiprocessing import Process
import pyodbc as pbc
import bcrypt as bpt

# login 0, register 1, get_contacts 2, get_conversations 3
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
                    data = data.decode().strip('\n').split('\n')
                    cmd, user_id = int(data[0]), data[1]
                    print(f"Received: {data}")
                    send_msg = give_data(cmd, db_conn, db_cursor, user_id, data)
                    conn.sendall(send_msg.encode())

def give_data(cmd, conn, cursor, user_id, data):
    if cmd == 0:
        """登录"""
        cursor.execute('SELECT UserID FROM Users WHERE Username = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute('SELECT PasswordHash FROM Users WHERE Username = ?', (user_id,))
            true_pwd = cursor.fetchone().PasswordHash
            pwd_from_user = data[2]
            if bpt.checkpw(pwd_from_user.encode(), true_pwd):
                return 'yes'
            else:
                return 'no'
        else:
            return 'unknown'

    elif cmd == 1:
        """注册"""
        password = bpt.hashpw(data[2].encode(), bpt.gensalt())    # 密码加密
        sql_insert = """
                INSERT INTO Users (Username, PasswordHash, Email)
                VALUES (?, ?, ?)
            """
        # 要插入的数据
        user_data = [
            user_id,  # 这里user_id参数默认在注册的时候Username
            password,  # PasswordHash
            data[3],  # Email
        ]
        # if len(data) > 4:
        #     user_data += data[4:]
        user_data = tuple(user_data)
        try:
            cursor.execute(sql_insert, user_data)
            conn.commit()
            print("User Register successfully.")
            return 'yes'
        except Exception as e:
            # 如果发生错误，回滚事务
            conn.rollback()
            print(f"An error occurred: {e}")
            return 'no'
    elif cmd == 2:
        """获取全部联系人名字"""
        contact_info = get_contacts(cursor, user_id)
        if contact_info:
            return contact_info
        else:
            return '\n'
    elif cmd == 3:
        query = '''
            WITH UserIDs AS (
                SELECT UserID FROM Users WHERE Username = ?
            ),
            LatestMessages AS (
                SELECT
                    m.MessageID,
                    m.SenderID,
                    m.ReceiverID,
                    u1.Username AS SenderName,
                    u2.Username AS ReceiverName,
                    m.Content,
                    m.SentAt,
                    m.IsRead,
                    ROW_NUMBER() OVER (
                        PARTITION BY 
                            CASE WHEN m.SenderID IN (SELECT UserID FROM UserIDs) THEN m.ReceiverID ELSE m.SenderID END -- 分区依据对方用户
                        ORDER BY m.SentAt DESC -- 按发送时间降序排列
                    ) AS rn
                FROM Messages_ m
                INNER JOIN Users u1 ON m.SenderID = u1.UserID
                INNER JOIN Users u2 ON m.ReceiverID = u2.UserID
                CROSS JOIN UserIDs
                WHERE m.SenderID IN (SELECT UserID FROM UserIDs) OR m.ReceiverID IN (SELECT UserID FROM UserIDs)
            )
            SELECT *
            FROM LatestMessages
            WHERE rn = 1
            ORDER BY SentAt DESC;
            '''
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        if rows:
            result = ''
            for row in rows:
                other_user = row.ReceiverName if row.SenderID == user_id else row.SenderName
                content = row.Content
                result += other_user + '  ' + content + '\n'
        else:
            result = '\n'
        return result



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
    server_ip_addr = '127.0.0.1'
    server_port = 65432
    buffer_size = 1024
    start_server(server_ip_addr, server_port, buffer_size)
