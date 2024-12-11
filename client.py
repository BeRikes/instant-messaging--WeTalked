import socket
import os
import time
# login 0, register 1, get_contacts 2


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
                message()
            elif cmd == 2:
                search_contact(s, user_id, buffer_size)
            elif cmd == 3:
                group()


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
        user_id = input("账号：")
        password = input("密码：")
        msg = login_cmd + '\n' + user_id + '\n' + password    # server通过login_cmd判断当前是登录还是注册信息
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
                os.system('cls')
                return user_id
            elif login_cmd == '1':
                print('账号注册成功')
                login_cmd = '0'
        elif data == 'no':
            print('账号或密码错误')
        elif data == 'unknown':
            print("该账号不存在，请先注册")
            if input("是否注册<yes/no>") == 'yes':
                login_cmd = '1'


def search_contact(s, user_id, buffer_size):
    send_msg = '2\n' + user_id
    s.sendall(send_msg.encode())  # 获取用户所有好友信息，并打印输出
    contacts = s.recv(2 * buffer_size).decode()
    contacts = contacts.strip('\n').split("\n")
    if len(contacts) > 0:
        print('好友：')
        for i, friend in enumerate(contacts):
            print(f"{i} {friend}   ")
    else:
        print('无好友')
    return contacts


def message():
    pass


def group():
    pass


if __name__ == "__main__":

    server_ip_addr = ''
    server_port = 65432
    buffer = 1024
    start_client(server_ip_addr, server_port, buffer)