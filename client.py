import socket
from client_utils.login_register import *
from client_utils.conversation import *
from client_utils.friends_groups import *


def start_client(host='127.0.0.1', port=65432, buffer_size=1024):
    """客户端socket程序(控制台)"""
    functions = ('消息', '联系人', '群聊', '加好友/群', '退出')
    # 创建一个socket对象
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        user_id = login(s, buffer_size)  # 先进入登录或注册界面
        if user_id is None:
            return
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


def start_client_with_gui(host, port, buffer_size):
    """客户端socket程序(GUI界面实现)"""
    from client_utils_gui.tk_login import Controller, Login
    # 创建一个socket对象
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        ctl = Controller(s, buffer_size)
        login = Login(ctl)
        login.mainloop()
    print('程序正常结束，所有资源均已释放，感谢您的使用')


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


if __name__ == "__main__":
    with open('./config.wtd', mode='r', encoding='utf-8') as f:
        server_ip_addr, server_port, buffer = f.read().strip('\n').split('-')
        server_port, buffer = int(server_port), int(buffer)
    start_client_with_gui(server_ip_addr, server_port, buffer)
