import socket
import os
import time

# 服务器要执行的操作+对应的指令id: login 0, register 1, get_contacts 2, get_conversations 3


def start_client(host='127.0.0.1', port=65432, buffer_size=1024):
    """客户端socket程序"""
    functions = ('消息', '联系人', '群聊', '退出')
    # 创建一个socket对象
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        user_id = login(s, buffer_size)  # 先进入登录或注册界面
        if user_id is None:
            return
        while True:
            cmd = menu(functions)
            if cmd == len(functions):
                return
            if cmd == 1:
                message(s, buffer_size, user_id)
                os.system('pause')
            elif cmd == 2:
                search_contact(s, buffer_size, user_id)
                os.system('pause')
            elif cmd == 3:
                group(s, buffer_size, user_id)
                os.system('pause')


def menu(func):
    """登录成功之后，程序的主菜单，功能界面"""
    os.system('cls')
    print("----WeTalked<Menv>----")
    for i, f in enumerate(func):
        print(i, f, end='   ')
    print("\n----WeTalked<Menv>----")
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
            print("---登录---")
        elif login_cmd == '1':
            print('---注册---')
        else:
            print("---------")
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


def search_contact(s, buffer_size, user_id):
    send_msg = '2\n' + user_id
    s.sendall(send_msg.encode())  # 获取用户所有好友信息，并打印输出
    contacts = s.recv(2 * buffer_size).decode()
    contacts = contacts.strip('\n').split("\n")
    if len(contacts) == 0 or contacts == ['']:
        print('无好友')
    else:
        print('好友：')
        for i, friend in enumerate(contacts):
            print(f"{i} {friend}   ")

    return contacts


def message(s, buffer, user_id):
    """输出用户的所有会话框，按时间排序，最新会话排在前面，会话内容为消息记录中最新的一条记录"""
    os.system('cls')
    send_msg = '3\n' + user_id
    s.sendall(send_msg.encode())
    data = s.recv(buffer).decode()
    data = data.strip('\n').split('\n')

    if len(data) == 0 or data == ['']:
        print("-------------------------------\n|当前无消息\n-------------------------------")
    else:
        print('-------------------------------')
        for item in data:
            print('|'+ item + '\n-------------------------------')


def group(s, buffer, user_id):
    os.system('cls')
    pass


if __name__ == "__main__":
    server_ip_addr = '127.0.0.1'
    server_port = 65432
    buffer = 1024
    start_client(server_ip_addr, server_port, buffer)