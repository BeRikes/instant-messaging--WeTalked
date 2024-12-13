import socket
from client_utils.login_register import *
from client_utils.conversation import *
from client_utils.friends_groups import *


# 服务器要执行的操作+对应的指令id:
# login 0, register 1, get_contacts 2, get_conversations 3, search user 4, insert friends 5, message_send_to 6
# search group by group id 7, insert groupMember 8, search_message_between 9, accept_friend_made_request 10


def start_client(host='127.0.0.1', port=65432, buffer_size=1024):
    """客户端socket程序"""
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
    server_ip_addr = '127.0.0.1'
    server_port = 65432
    buffer = 1024
    start_client(server_ip_addr, server_port, buffer)