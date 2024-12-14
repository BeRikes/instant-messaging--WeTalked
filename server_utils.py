from datetime import datetime, timedelta
import bcrypt as bpt


system_User_name = 'we_talked'

def give_data(cmd, conn, cursor, user_id, data):
    if cmd == 0:
        """登录"""
        if user_id == system_User_name:
            return 'no'
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
        if user_id == system_User_name:
            return 'no'
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
        if len(data) > 4:
            sql_insert = """
                INSERT INTO Users (Username, PasswordHash, Email, PhoneNumber)
                VALUES (?, ?, ?, ?)
            """
            user_data.append(data[4])   # PhoneNumber
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
            return '$'    # 无联系人
    elif cmd == 3:
        """获取当前帐号历史会话"""
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
                other_user = row.ReceiverName if row.SenderName == user_id else row.SenderName
                content = row.Content
                result += str(row.MessageID) + '$' + other_user + '$' + content + '\n'
        else:
            result = '$'
        return result.rstrip('\n')
    elif cmd == 4:
        """查找好友"""
        add_name, add_email = data[1], data[2]
        if add_name != '$':
            query = """
                SELECT Username, Email, PhoneNumber, CreatedAt, LastLogin
                FROM Users
                WHERE Username = ?
                """
            cursor.execute(query, (add_name,))
        else:
            query = """
                SELECT Username, Email, PhoneNumber, CreatedAt, LastLogin
                FROM Users
                WHERE Email = ?
                """
            cursor.execute(query, (add_email,))
        row = cursor.fetchone()
        if row:
            info_list = [row.Username, row.Email, row.PhoneNumber, row.CreatedAt.strftime('%Y-%m-%d %H:%M:%S'), row.LastLogin]
            if info_list[2] is None:
                info_list[2] = '电话号未知'
            if info_list[4] is None:
                info_list[4] = '最后登陆时间未知'
            return '  '.join(info_list)
        else:
            return '$'

    elif cmd == 5:
        """添加好友"""
        add_name = data[2]
        finish_add = True
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        sender_id = cursor.execute(query_user_id, (user_id,)).fetchone()
        receiver_id = cursor.execute(query_user_id, (add_name,)).fetchone()
        insert_friend = """
            INSERT INTO Friendships (User1ID, User2ID, Status_)
            VALUES (?, ?, 'Pending');
            """
        try:
            cursor.execute(insert_friend, (sender_id.UserID, receiver_id.UserID))
            conn.commit()
            print("User friend made successfully.")
        except Exception as e:
            # 如果发生错误，回滚事务
            conn.rollback()
            print(f"An error occurred: {e}")
            finish_add = False
        if finish_add:
            send_message_to(conn, cursor, system_User_name, add_name, f"{user_id}请求添加好友")
            return 'pending'
        else:
            return 'no'
    elif cmd == 6:
        if send_message_to(conn, cursor, user_id, data[2], data[3]):
            return 'yes'
        else:
            return 'no'
    elif cmd == 7:
        pass
    elif cmd == 8:
        pass
    elif cmd == 9:
        another, after, pre_time = data[2], data[3], data[4]
        # 查询发送者和接收者的UserID
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        sender_id = cursor.execute(query_user_id, (user_id,)).fetchone()
        receiver_id = cursor.execute(query_user_id, (another,)).fetchone()
        id_to_name = {sender_id.UserID: '我', receiver_id.UserID: "对方"}
        if not sender_id or not receiver_id:
            print("发送者或接收者不存在")
            return None
        # 查询消息
        query_messages = """
                    SELECT MessageID, SenderID, Content, SentAt
                    FROM Messages_
                    WHERE ((SenderID = ? AND ReceiverID = ?) OR (SenderID = ? AND ReceiverID = ?))
                    AND MessageID > ?
                    ORDER BY MessageID;
                    """
        cursor.execute(query_messages, (sender_id.UserID, receiver_id.UserID,
                                        receiver_id.UserID, sender_id.UserID,
                                        int(after)))
        # 获取所有符合条件的消息
        rows = cursor.fetchall()
        if rows:
            msg = ''
            # 定义一个时间增量（这里是减去5分钟）
            time_delta = timedelta(minutes=5)
            pre_time = datetime.strptime(pre_time, '%Y-%m-%d %H:%M:%S')
            for row in rows:
                if row.SentAt - pre_time >= time_delta:
                    msg += row.SentAt.strftime('%Y-%m-%d %H:%M:%S') + '\n'
                    pre_time = row.SentAt
                msg += id_to_name[row.SenderID] + ':' + row.Content + '\n'
            msg = msg.rstrip()
            after = str(int(rows[-1].MessageID))
            pre_time = datetime.strftime(pre_time, '%Y-%m-%d %H:%M:%S')
            return after + '$' + msg + '$' + pre_time
        else:
            return after + '$' + 'no news' + '$' + pre_time
    elif cmd == 10:
        another, messageID = data[2], data[3]
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        sender_id = cursor.execute(query_user_id, (user_id,)).fetchone()
        receiver_id = cursor.execute(query_user_id, (another,)).fetchone()
        if not sender_id or not receiver_id:
            print("发送者或接收者不存在")
            return '发送者或接收者不存在'
        update_sql = """
                UPDATE Friendships
                SET Status_ = 'Accepted'
                WHERE User1ID = ? AND User2ID = ? AND Status_ = 'Pending';
            """
        try:
            updated_rows = cursor.execute(update_sql, (sender_id.UserID, receiver_id.UserID)).rowcount
            # 如果双向好友关系都被存储，则需要考虑两个方向的记录
            updated_rows += cursor.execute(update_sql, (receiver_id.UserID, sender_id.UserID)).rowcount
            conn.commit()  # 提交事务以保存更改
            if updated_rows > 0:
                delete_result = delete_one_message(conn, cursor, messageID)
                if delete_result == 1:
                    return 'yes'
                elif delete_result == 0:
                    raise '未找到该信息'
                else:
                    raise '删除消息时，出现错误，请重试'
            else:
                return '没有找到待处理的好友申请'
        except Exception as e:
            conn.rollback()
            print(f"An error occurred: {e}")


def get_contacts(db_cursor, user_name):
    """获取user_name用户的所有联系人姓名"""
    sql_query = """
    WITH UserIDs AS (
        SELECT UserID FROM Users WHERE Username = ?
    ),
    FilteredFriendships AS (
        SELECT
            CASE
                WHEN F.User1ID = (SELECT UserID FROM UserIDs) THEN U2.Username
                ELSE U1.Username
            END AS FriendName
        FROM
            Friendships F
        JOIN
            Users U1 ON F.User1ID = U1.UserID
        JOIN
            Users U2 ON F.User2ID = U2.UserID
        CROSS JOIN UserIDs
        WHERE
            (F.User1ID = (SELECT UserID FROM UserIDs) OR F.User2ID = (SELECT UserID FROM UserIDs))
            AND F.Status_ = 'Accepted'
    )
    SELECT DISTINCT FriendName FROM FilteredFriendships;
    """
    db_cursor.execute(sql_query, (user_name,))
    rows = db_cursor.fetchall()
    if rows:
        msg = ''
        for row in rows:
            msg += row.FriendName + '\n'
        return msg.rstrip('\n')
    else:
        return None

def send_message_to(conn, cursor, sender_username, receiver_username, message_content):
    query_user_ids = "SELECT UserID FROM Users WHERE Username = ?;"
    sender = cursor.execute(query_user_ids, (sender_username,)).fetchone()
    receiver = cursor.execute(query_user_ids, (receiver_username,)).fetchone()
    if not sender or not receiver:
        print("发送者或接收者不存在")
        return False
    # 插入消息到Messages_表
    insert_message_query = """
                    INSERT INTO Messages_ (SenderID, ReceiverID, Content)
                    VALUES (?, ?, ?);
                    """
    try:
        cursor.execute(insert_message_query, (sender.UserID, receiver.UserID, message_content))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return False
    return True


def delete_one_message(conn, cursor, messageID):
    # 删除Messages_表中指定发送者和接收者之间的所有消息
    delete_messages_query = """
        DELETE FROM Messages_
        WHERE MessageID = ?;
        """
    try:
        deleted_rows = cursor.execute(delete_messages_query, (messageID,)).rowcount
        conn.commit()  # 提交事务以保存更改
        if deleted_rows > 0:
            print(f'成功删除信息 MessageID = {messageID}')
            return 1
        else:
            print('未找到该信息')
            return 0
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return -1
