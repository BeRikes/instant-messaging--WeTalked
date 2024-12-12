import socket
import os
import time
import threading

# 服务器要执行的操作+对应的指令id:
# login 0, register 1, get_contacts 2, get_conversations 3, search user 4, insert friends 5, message_send_to 6
# search group by group id 7, insert groupMember 8, search_message_between 9


def start_client(host='127.0.0.1', port=65432, buffer_size=1024):
    """客户端socket程序"""
    functions = ('消息', '联系人', '群聊', '加好友/群', '退出')
    # 创建一个socket对象
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        user_id = login(s, buffer_size)  # 先进入登录或注册界面
        if user_id is None:
            return
        # # 在主程序开始时启动新的线程来接收消息
        # recv_thread = threading.Thread(target=receive_messages, args=(s, buffer_size))
        # recv_thread.daemon = True  # 设置为守护线程，当主线程结束时自动退出
        # recv_thread.start()
        while True:
            cmd = menu(functions, user_id)
            if cmd == len(functions):
                return
            if cmd == 1:
                message(s, buffer_size, user_id)
                input("输入任意键，返回菜单......")
            elif cmd == 2:
                contact(s, buffer_size, user_id)
                input("输入任意键，返回菜单......")
            elif cmd == 3:
                group(s, buffer_size, user_id)
                input("输入任意键，返回菜单......")
            elif cmd == 4:
                add_friend_or_group(s, buffer_size, user_id)
                input('输入任意键，返回菜单......')



# def receive_messages(sock, buffer_size):
#     while True:
#         try:
#             # 假设message_handler是处理接收到的消息的函数
#             message = sock.recv(buffer_size)
#             if not message:
#                 print("连接被关闭")
#                 break
#             # 处理来自服务端发送的新消息
#             message = message.decode().split('\n')
#             print(f'{message[0]}: {message[1]}')
#         except Exception as e:
#             print(f"接收消息时发生错误: {e}")
#             break


def menu(func, user_id):
    """登录成功之后，程序的主菜单，功能界面"""
    os.system('cls')
    print("-----WeTalked<Menv>-----")
    print(f'--------{user_id}--------')
    for i, f in enumerate(func):
        print(i + 1, f, end='   ')
    print("\n-----WeTalked<Menv>-----")
    cmd = int(input())
    while cmd > len(func):
        print('无此功能, 请重新输入!')
        cmd = int(input())
    return cmd


def login(s, buffer_size):
    login_cmd = '0'
    data = 'no'
    while data != 'yes':
        if login_cmd == '0':
            print("-----登录-----")
        elif login_cmd == '1':
            print('-----注册-----')
        else:
            print("-------------")
        user_id = input('用户名：')
        password = input("密码：")     # 有待加密
        msg = login_cmd + '\n' + user_id + '\n' + password
        if login_cmd == '1':
            email = input("邮箱：")
            phoneNumber = input('电话号码(输入-1,表示不填)：')
            msg += '\n' + email
            if phoneNumber != '-1': msg += '\n' + phoneNumber
        s.sendall(msg.encode())
        print("正在检查账号和密码")
        data = s.recv(buffer_size).decode()
        if not data:
            print('服务器关闭了与你的连接，请检查网络状态')
            return None
        if data == 'yes':
            if login_cmd == '0':
                print('登录成功, 密码正确')
                time.sleep(3)
                return user_id
            elif login_cmd == '1':
                print('账号注册成功')
                time.sleep(3)
                login_cmd = '0'
                data = 'no'
        elif data == 'no':
            if login_cmd == '0': print('账号或密码错误!')
            else: print('请换一个用户名或者邮箱!')
        elif data == 'unknown':
            print("该账号不存在，请先注册")
            if input("是否注册<yes/no>") == 'yes':
                login_cmd = '1'


def contact(s, buffer_size, user_id):
    contacts = search_contact(s, buffer_size, user_id)
    if contacts is None:
        return
    choice = int(input("选择联系人或者输入0，返回菜单......")) - 1
    while choice >= len(contacts) or choice < -1:
        print('无此联系人，请重新输入')
        choice = int(input("选择联系人或者输入0，返回菜单......"))
    if choice != -1:
        talk_with_another(s, buffer_size, user_id, contacts[choice])


def search_contact(s, buffer_size, user_id):
    send_msg = '2\n' + user_id
    s.sendall(send_msg.encode())  # 获取用户所有好友信息，并打印输出
    contacts = s.recv(buffer_size).decode()
    contacts = contacts.split("\n")
    if len(contacts) == 1 and contacts[0] == '$':
        print('无好友')
        return None
    else:
        print('好友：')
        for i, friend in enumerate(contacts):
            print(f"{i + 1} {friend}   ")
        return contacts


def talk_with_another(s, buffer_size, user_name, another_name):
    print(f'talking with {user_name}, $ + ENTER 返回联系人目录')
    # 多线程查询当前信息
    stop_event = threading.Event()
    convers_thread = threading.Thread(target=conversation_content_update, args=(stop_event, s, buffer_size, user_name, another_name))
    # convers_thread.daemon = True  # 设置为守护线程，当主线程结束时自动退出
    convers_thread.start()
    try:
        while True:
            send_msg = input('我：')
            if send_msg == '$':
                break
            send_msg = '6\n' + user_name + '\n' + another_name + '\n' + send_msg
            s.sendall(send_msg.encode())
            data = s.recv(buffer_size).decode()
            if data == 'no':
                print('此消息发送失败!')
    finally:
        # 确保在离开test函数之前发出停止信号
        stop_event.set()
        # 等待线程结束，可以加个超时时间避免阻塞过久
        convers_thread.join(timeout=4)  # 超时时间为5秒


def conversation_content_update(stop_event, s: socket.socket, buffer_size, user_name, another):
    after = '2020-01-01 00:00:00'
    while not stop_event.is_set():
        msg = '9\n' + user_name + '\n' + another + '\n' + after
        s.sendall(msg.encode())
        data = s.recv(buffer_size).decode()
        gap_idx = data.find('\n')
        after = data[:gap_idx]
        if len(data[gap_idx + 1:]) != 7 or data[gap_idx + 1:] != 'no news':
            print(data[gap_idx + 1:])
        time.sleep(5)


def message(s, buffer, user_id):
    """输出用户的所有会话框，按时间排序，最新会话排在前面，会话内容为消息记录中最新的一条记录"""
    os.system('cls')
    send_msg = '3\n' + user_id
    s.sendall(send_msg.encode())
    data = s.recv(buffer).decode()
    data = data.split('\n')

    if len(data) == 1 and data[0] == '$':
        print("-------------------------------\n|当前无消息\n-------------------------------")
    else:
        print('-------------------------------')
        for item in data:
            print('|'+ item + '\n-------------------------------')


def group(s, buffer, user_id):
    os.system('cls')
    pass


def add_friend_or_group(s, buffer_size, user_id):
    os.system('cls')
    while True:
        choice = int(input('0 加好友, 1 加群聊'))
        if choice == 0:
            add_new_friend(s, buffer_size, user_id)
            break
        elif choice == 1:
            join_in_group(s, buffer_size, user_id)
            break


def add_new_friend(s, buffer_size, user_id):
    print('请输入想添加的用户名或者邮箱，$表示不填')
    while True:
        add_name = input("用户名：")
        add_email = input('邮箱：')
        if add_name == '': add_name = '$'
        if add_email == '': add_email = '$'
        if add_name == '$' and add_email == '$':
            print('请填入内容，不可为空')
            continue
        send_msg = '4\n' + add_name + '\n' + add_email
        s.sendall(send_msg.encode())
        data = s.recv(buffer_size).decode()         # 查询结果
        if data == '$':
            print('无此用户')
            break
        else:
            print('你要找的用户如下：')          # 由于数据库中限制了用户名唯一，邮箱唯一，因此只可能找到一个匹配的用户
            print('---------------------\n|', data, '\n---------------------')
            add_if = input("是否添加？[yes/no] 其他输入则继续搜索用户")
            if add_if == 'no':
                break
            elif add_if == 'yes':
                data = data.split('  ')
                send_msg = '5\n' + user_id + '\n' + data[0]
                s.sendall(send_msg.encode())
                data = s.recv(buffer_size).decode()
                # if data == 'yes':
                #     print("好友添加成功")
                #     break
                if data == 'pending':
                    print('等待对方确认')
                    break
                else:
                    print('好友添加失败')
                    break


def join_in_group(s, buffer_size, user_id):
    print('请输入想添加的群聊名称，$表示不填')
    while True:
        group_name = input('群聊昵称：')
        if group_name == '': group_name = '$'
        if group_name == '$':
            print('输入内容为空')
            continue
        send_msg = '7\n' + group_name
        s.sendall(send_msg)
        data = s.recv(2 * buffer_size).decode().split('\n')      # 用\n隔开的群聊列表项(id$...)
        if data == ['']:
            print('没找到该群聊')
        else:
            print('--------群聊列表--------')
            content_idx = [item.find('$') + 1 for item in data]
            for i, item in enumerate(data):
                print('|', i + 1, item[content_idx[i]:])
                print('------------------------')
            while True:
                idx = int(input('选择一个群聊: (禁止选不存在)')) - 1
                if idx > len(data): continue
                group_id = data[idx][:content_idx[idx] - 1]
                send_msg = '8\n' + group_id
                s.sendall(send_msg.encode())
                join_in_result = s.recv(buffer_size).decode()
                if join_in_result == 'yes':
                    print("群聊加入成功")
                elif join_in_result == 'no':
                    print('群聊加入失败')
                elif join_in_result == 'pending':     # 服务器先给群主发送{用户加群请求}的消息，群主何时同意，用户何时能加入群聊
                    print('需要群主审核，等待后续通知')
                break




if __name__ == "__main__":
    server_ip_addr = '127.0.0.1'
    server_port = 65432
    buffer = 1024
    start_client(server_ip_addr, server_port, buffer)