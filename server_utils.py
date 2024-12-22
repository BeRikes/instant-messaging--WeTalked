from datetime import datetime, timedelta
import bcrypt as bpt

# 服务器要执行的操作+对应的指令id:
# login 0, register 1, get_contacts 2, get_conversations 3, search user 4, insert friends 5, message_send_to 6
# search group by group id 7, insert groupMember 8, search_message_between 9, accept_friend_made_request 10
# user_exit 11, request file_instant_trans 12, accept_file_trans 13, create_group 14, accept_group_join_request 15
# search_group_members 16, get_groups 17, search_message_group 18, message_to_group 19
system_User_name = 'we_talked'


def give_data(cmd, conn, cursor, user_name, data, username2addr):
    if cmd == 0:
        """登录"""
        if user_name == system_User_name:
            return 'no'
        cursor.execute('SELECT UserID FROM Users WHERE Username = ?', (user_name,))
        row = cursor.fetchone()
        if row:
            cursor.execute('SELECT PasswordHash FROM Users WHERE Username = ?', (user_name,))
            true_pwd = cursor.fetchone().PasswordHash
            pwd_from_user = data[2]
            if bpt.checkpw(pwd_from_user.encode(), true_pwd):
                try:
                    update_cnt = cursor.execute('UPDATE Users SET IsActive = 1 WHERE Username = ?', (user_name,)).rowcount
                    conn.commit()
                    if update_cnt > 0:
                        return 'yes'
                    else:
                        return 'no'
                except Exception as e:
                    conn.rollback()
                    print(f"An error occurred: {e}")
            else:
                return 'no'
        else:
            return 'unknown'

    elif cmd == 1:
        """注册"""
        if user_name == system_User_name:
            return 'no'
        password = bpt.hashpw(data[2].encode(), bpt.gensalt())    # 密码加密
        sql_insert = """
                INSERT INTO Users (Username, PasswordHash, Email)
                VALUES (?, ?, ?)
            """
        # 要插入的数据
        user_data = [
            user_name,  # 这里user_name参数默认在注册的时候Username
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
        contact_info = get_contacts(cursor, user_name)
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
        cursor.execute(query, (user_name,))
        rows = cursor.fetchall()
        if rows:
            result = ''
            for row in rows:
                other_user = row.ReceiverName if row.SenderName == user_name else row.SenderName
                content = row.Content
                result += str(row.MessageID) + '$' + other_user + '$' + content + '\n'    # 加入messageID是为了删除系统通知
        else:
            result = '$'
        return result.rstrip('\n')
    elif cmd == 4:
        """查找好友"""
        add_name, add_email = data[1], data[2]
        if add_name != '$' and add_email != '$':
            query = """
                SELECT Username, Email, PhoneNumber, CreatedAt, LastLogin
                FROM Users
                WHERE Username = ? AND Email = ?
                """
            cursor.execute(query, (add_name, add_email))
        elif add_name != '$':
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
        sender_id = cursor.execute(query_user_id, (user_name,)).fetchone()
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
        if finish_add and send_message_to(conn, cursor, system_User_name, add_name, f"{user_name}请求添加好友"):
            return 'pending'
        else:
            return 'no'
    elif cmd == 6:
        if send_message_to(conn, cursor, user_name, data[2], data[3]):
            return 'yes'
        else:
            return 'no'
    elif cmd == 7:
        """根据群聊名称来查找群聊, 返回所有查询结果"""
        group_name = data[1]
        query = """
                SELECT GroupID, GroupName, OwnerID, CreatedAt, Description
                FROM Groups
                WHERE GroupName = ?
                ORDER BY OwnerID;
                """
        cursor.execute(query, (group_name,))
        rows = cursor.fetchall()
        if rows:
            msg = ''
            for row in rows:
                cursor.execute('SELECT Username From Users WHERE UserID = ?', (row.OwnerID,))
                owner_name = cursor.fetchone().Username
                msg += str(row.GroupID) + '$' + row.GroupName + '  ' + owner_name + '  ' + row.CreatedAt.strftime(
                    '%Y-%m-%d %H:%M:%S')
                if not row.Description:
                    msg += '  ' + row.Description
                msg += '\n'
            return msg.rstrip('\n')
        else:
            return '$'
    elif cmd == 8:
        """加入群聊或邀请加入群聊"""
        group_id, group_name = data[2], data[3]
        another_name = data[4]
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        user_id = cursor.execute(query_user_id, (user_name,)).fetchone().UserID
        another_id = cursor.execute(query_user_id, (another_name,)).fetchone().UserID
        system_user_id = cursor.execute(query_user_id, (system_User_name,)).fetchone().UserID
        insert_sql = """
                    INSERT INTO GroupMembers (GroupID, MemberID, Status_)
                    VALUES (?, ?, 'Pending');
                    """
        try:
            cursor.execute(insert_sql, (group_id, user_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"An error occurred: {e}")
            return 'no'
        owner_id = cursor.execute('SELECT OwnerID FROM Groups WHERE GroupID = ?;', (group_id,)).fetchone().OwnerID
        if user_id == owner_id:
            # 由群主用户发出的加群邀请，信息发送对象为非群主
            receiver_id = another_id
            if send_message_to(conn, cursor, system_user_id, receiver_id, f'{user_name}邀请您加入群聊{group_name}[{group_id}]'):
                return 'pending'
            else:
                return 'no'
        else:
            # 由非群主用户发起的加入群聊申请，信息发送对象为群主
            receiver_id = owner_id
            if send_message_to(conn, cursor, system_user_id, receiver_id, f'{user_name}请求加入群聊{group_name}[{group_id}]'):
                return 'pending'
            else:
                return 'no'
    elif cmd == 9:
        another, after, pre_time = data[2], data[3], data[4]
        # 查询发送者和接收者的UserID
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        sender_id = cursor.execute(query_user_id, (user_name,)).fetchone()
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
        sender_id = cursor.execute(query_user_id, (user_name,)).fetchone()
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
    elif cmd == 11:
        try:
            update_cnt = cursor.execute('UPDATE Users SET IsActive = 0 WHERE Username = ?', (user_name,)).rowcount
            conn.commit()
            if update_cnt > 0:
                return 'yes'
            else:
                return 'no'
        except Exception as e:
            conn.rollback()
            print(f"An error occurred: {e}")
    elif cmd == 12:
        """发送文件即时传输请求(系统消息)"""
        if send_message_to(conn, cursor, system_User_name, data[2], f'{user_name}请求文件传输{data[3]}'):
            return 'pending'
        else:
            return 'no'
    elif cmd == 13:
        """同意文件即时传输"""
        another, messageID = data[2], data[3]
        cursor.execute('SELECT IsActive FROM Users WHERE Username = ?', (another,))
        row = cursor.fetchone()
        if not row.IsActive:
            return '-1'  # 目标不在线
        delete_result = delete_one_message(conn, cursor, messageID)
        if delete_result == 1:
            another_ip, another_port = username2addr[another]
            return another_ip + '\n' + str(another_port)
        elif delete_result == 0:
            return '0'   # 未找到该信息
        else:
            return '1'   # 删除消息时，出现错误，请重试
    elif cmd == 14:
        """创建群聊"""
        group_name = data[2]
        group_description = data[3]
        if len(data) > 4:
            group_members = data[4:0]
        if group_name == system_User_name:
            return 'invalid'
        finish_add = True
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        owner_id = cursor.execute(query_user_id, (user_name,)).fetchone()
        create_group = """
                INSERT INTO Groups (GroupName, OwnerID, Description)
                OUTPUT INSERTED.GroupID
                VALUES (?, ?, ?);
            """
        try:
            group_ids = cursor.execute(create_group, (group_name, owner_id.UserID, group_description)).fetchone()
            group_id = group_ids.GroupID
            print("New Group Create successfully.")
            create_owner = """
                    INSERT INTO GroupMembers (GroupID, MemberID, IsAdmin, Status_)
                    VALUES (?, ?, 1, 'Accepted');
                """
            cursor.execute(create_owner, (group_id, owner_id.UserID))
            conn.commit()
            return 'success'
        except Exception as e:
            # 如果发生错误，回滚事务
            conn.rollback()
            print(f"An error occurred: {e}")
            return 'no'
    elif cmd == 15:
        """进群申请/邀请审核"""
        group_id = data[3]
        another_name = data[2]
        messageID = data[4]
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        sender_id = cursor.execute(query_user_id, (user_name,)).fetchone()
        receiver_id = cursor.execute(query_user_id, (another_name,)).fetchone()
        if not sender_id or not receiver_id:
            return '发送者或接收者不存在'

        query_member = """
            UPDATE GroupMembers
            SET Status_ = 'Accepted'
            WHERE GroupID = ? AND (MemberID = ? OR MemberID = ?) AND IsAdmin = 0 AND Status_ = 'Pending';
        """
        try:
            updated_rows = cursor.execute(query_member, (group_id, sender_id.UserID, receiver_id.UserID)).rowcount
            conn.commit()  # 提交事务以保存更改
            if updated_rows > 0:
                delete_result = delete_one_message(conn, cursor, messageID)
                if delete_result == 1:
                    return 'accept'
                elif delete_result == 0:
                    return '未发现当前群聊申请'
                else:
                    return '删除消息时出现错误，请重试'
            else:
                return '没有找到待处理的好友申请'
        except Exception as e:
            conn.rollback()
            print(f"An error occurred: {e}")
            return 'no'
    elif cmd == 17:
        """获取全部群聊信息"""
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        user_id = cursor.execute(query_user_id, (user_name,)).fetchone().UserID
        contact_info = get_groups(cursor, user_id)
        if contact_info:
            return contact_info
        else:
            return '$'  # 无联系人
    elif cmd == 18:
        group_id, after, pre_time = data[2], data[3], data[4]
        # 查询消息
        query_messages = """
            SELECT GroupMessageID, SenderID, Content, SentAt
            FROM GroupMessages
            WHERE GroupID = ?
            AND GroupMessageID > ?
            ORDER BY GroupMessageID;
        """
        cursor.execute(query_messages, (group_id, int(after)))
        # 获取所有符合条件的消息
        rows = cursor.fetchall()
        if rows:
            msg = ''
            # 定义一个时间增量（这里是减去5分钟）
            time_delta = timedelta(minutes=5)
            pre_time = datetime.strptime(pre_time, '%Y-%m-%d %H:%M:%S')
            id_dist = {}
            for row in rows:
                sender_id = row.SenderID
                if row.SentAt - pre_time >= time_delta:
                    msg += row.SentAt.strftime('%Y-%m-%d %H:%M:%S') + '\n'
                    pre_time = row.SentAt
                if sender_id in id_dist:
                    sender_name = id_dist[sender_id]
                else:
                    query_user_name = "SELECT Username FROM Users WHERE UserID = ?;"
                    sender_name = cursor.execute(query_user_name, (sender_id,)).fetchone().Username
                    id_dist[sender_id] = sender_name
                msg += sender_name + ':' + row.Content + '\n'
            msg = msg.rstrip()
            after = str(int(rows[-1].GroupMessageID))
            pre_time = datetime.strftime(pre_time, '%Y-%m-%d %H:%M:%S')
            return after + '$' + msg + '$' + pre_time
        else:
            return after + '$' + 'no news' + '$' + pre_time
    elif cmd == 19:
        query_user_id = "SELECT UserID FROM Users WHERE Username = ?;"
        user_id = cursor.execute(query_user_id, (user_name,)).fetchone().UserID
        if send_message_to_group(conn, cursor, user_id, data[2], data[3]):
            return 'yes'
        else:
            return 'no'
    else:
        print("错误：未知的操作类型")
        return 'no'


def get_contacts(db_cursor, user_name):
    """获取user_name用户的所有联系人姓名和是否在线"""
    sql_query = """
    WITH UserIDs AS (
        SELECT UserID FROM Users WHERE Username = ?
    ),
    FilteredFriendships AS (
        SELECT
            CASE
                WHEN F.User1ID = (SELECT UserID FROM UserIDs) THEN U2.Username
                ELSE U1.Username
            END AS FriendName,
            CASE
                WHEN F.User1ID = (SELECT UserID FROM UserIDs) THEN U2.IsActive
                ELSE U1.IsActive
            END AS IsActive
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
    SELECT DISTINCT FriendName, IsActive
    FROM FilteredFriendships;
    """
    db_cursor.execute(sql_query, (user_name,))
    rows = db_cursor.fetchall()
    if rows:
        msg = ''
        for row in rows:
            msg += row.FriendName + '$' + str(row.IsActive) + '\n'
        return msg.rstrip('\n')
    else:
        return None


def get_groups(db_cursor, user_name):
    query_group = '''
    DECLARE @member_id INT = ?;

    WITH UserGroups AS (
        SELECT 
            g.GroupID,
            g.GroupName
        FROM Groups g
        JOIN GroupMembers gm ON g.GroupID = gm.GroupID
        WHERE gm.MemberID = @member_id AND gm.Status_ = 'Accepted'
    ),

    LatestMessages AS (
        SELECT 
            gm.GroupID,
            gm.SenderID,
            gm.Content AS LastMessageText,
            gm.SentAt AS LastMessageTime
        FROM GroupMessages gm
        INNER JOIN (
            SELECT GroupID, MAX(SentAt) AS MaxSentAt
            FROM GroupMessages
            GROUP BY GroupID
        ) AS max_gm ON gm.GroupID = max_gm.GroupID AND gm.SentAt = max_gm.MaxSentAt
    )

    -- 最终选择结果并排序
    SELECT 
        ug.GroupID,
        ug.GroupName,
        COALESCE(lm.LastMessageText, '') AS LastMessageText,
        COALESCE(lm.LastMessageTime, '1900-01-01') AS LastMessageTime
    FROM UserGroups ug
    LEFT JOIN LatestMessages lm ON ug.GroupID = lm.GroupID
    ORDER BY 
        COALESCE(lm.LastMessageTime, '1900-01-01') DESC;
    '''
    db_cursor.execute(query_group, (user_name, ))
    rows = db_cursor.fetchall()
    if rows:
        msg = ''
        for row in rows:
            msg += row.GroupName + '$' + str(row.GroupID) + '$' + row.LastMessageText + '\n'
        return msg.rstrip('\n')
    else:
        return None


def send_message_to(conn, cursor, sender_username, receiver_username, message_content):
    assert type(sender_username) == type(receiver_username), 'wrong type'
    if not isinstance(sender_username, int) and not isinstance(receiver_username, int):
        query_user_ids = "SELECT UserID FROM Users WHERE Username = ?;"
        sender = cursor.execute(query_user_ids, (sender_username,)).fetchone()
        receiver = cursor.execute(query_user_ids, (receiver_username,)).fetchone()
        if not sender or not receiver:
            print("发送者或接收者不存在")
            return False
        sender, receiver = sender.UserID, receiver.UserID
    else:
        sender, receiver = sender_username, receiver_username
    # 插入消息到Messages_表
    insert_message_query = """
                    INSERT INTO Messages_ (SenderID, ReceiverID, Content)
                    VALUES (?, ?, ?);
                    """
    try:
        cursor.execute(insert_message_query, (sender, receiver, message_content))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return False
    return True


def send_message_to_group(conn, cursor, sender_id, group_id, message_content):
    """向群聊中发送消息"""
    sender, group = sender_id, group_id
    # 插入消息到Messages_表
    insert_message_query = """
                    INSERT INTO GroupMessages (SenderID, groupID, Content)
                    VALUES (?, ?, ?);
                    """
    try:
        cursor.execute(insert_message_query, (sender, group, message_content))
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
