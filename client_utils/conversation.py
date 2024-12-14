import threading
import time
import os
import sys
from tk_ui.tk_talk_with_one import Win, Controller

def contact(s, buffer_size, user_id):
    contacts = search_contact(s, buffer_size, user_id)
    if contacts is None:
        return
    choice = input("选择联系人或者输入-1，返回菜单......")
    if choice == '':
        return
    choice = int(choice)
    while choice > len(contacts) or choice < -1:
        print('无此联系人，请重新输入')
        choice = input("选择联系人或者输入-1，返回菜单......")
        if choice == '': return
        choice = int(choice)
    if choice != -1:
        # talk_with_another(s, buffer_size, user_id, contacts[choice - 1])
        talk_with_another_gui(s, buffer_size, user_id, contacts[choice - 1])


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
    print(f'talking with {another_name}, $ + ENTER 返回联系人目录')
    # 多线程查询当前信息
    stop_event = threading.Event()
    socket_lock, print_lock = threading.Lock(), threading.Lock()
    convers_thread = threading.Thread(target=conversation_content_update, args=(stop_event, socket_lock, print_lock, s, buffer_size, user_name, another_name))
    convers_thread.start()
    try:
        while True:
            send_msg = input()
            with print_lock:
                clear_last_line()
            if send_msg == '$':
                break
            send_msg = '6\n' + user_name + '\n' + another_name + '\n' + send_msg
            s.sendall(send_msg.encode())
            with socket_lock:
                data = s.recv(buffer_size).decode()
            if data == 'no':
                print('此消息发送失败!')
    finally:
        # 确保在离开test函数之前发出停止信号
        stop_event.set()
        # 等待线程结束，可以加个超时时间避免阻塞过久
        convers_thread.join(timeout=5)  # 超时时间为5秒


def talk_with_another_gui(s, buffer_size, user_name, another_name):
    os.system('cls')
    print('see GUI')
    ctl = Controller(s, buffer_size, user_name, another_name)
    stop_event = threading.Event()
    win = Win(ctl)
    convers_thread = threading.Thread(target=ctl.insert_his_msg, args=(stop_event,))
    convers_thread.start()
    try:
        win.mainloop()
    finally:
        stop_event.set()
        convers_thread.join(timeout=5)

def conversation_content_update(stop_event, lock1, lock2, s, buffer_size, user_name, another):
    after = '0'
    pre_time = '2020-01-01 00:00:00'
    while not stop_event.is_set():
        msg = '9\n' + user_name + '\n' + another + '\n' + after + '\n' + pre_time
        s.sendall(msg.encode())
        with lock1:    # 防止与主进程之间竞争缓冲区
            data = s.recv(4 * buffer_size)    # 历史消息比较多，缓冲设置大
        data = data.decode().split('\n')
        after, content, pre_time = data
        if len(content) != 7 and content != 'no news':
            with lock2:
                print(content)
        time.sleep(2)


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
        id_idx = [item.find('$') + 1 for item in data]
        print('-------------------------------')
        for i, item in enumerate(data):
            print('|', i + 1, item[id_idx[i]:].replace('$', '  ') + '\n-------------------------------')
        # 决定是否同意系统通知(如we_talked: xxx请求添加好友), 或者与一个好友开始通讯
        choice = input("选择一个会话，开始通讯，输入-1返回菜单")
        if choice == '':
            return
        choice = int(choice)
        while choice < -1 or choice > len(data):
            choice = int(input("请重新输入，输入-1返回菜单"))
        if choice == -1:
            return
        msg_id, another, content = data[choice - 1].split('$')
        if another == 'we_talked':
            if content.find('添加好友') != -1:
                another = content[:-6]
                send_msg = '10\n' + user_id + '\n' + another + '\n' + msg_id
                s.sendall(send_msg.encode())
                data2 = s.recv(buffer).decode()
                if data2 == 'yes':
                    print(another + '现在是你的好友了!')
                else:
                    print('操作失败，失败原因:', data2)
        else:
            talk_with_another_gui(s, buffer, user_id, another)


def clear_last_line():
    """Clear the last line in the terminal."""
    # Move cursor up one line
    sys.stdout.write('\x1b[1A')
    # Delete last line
    sys.stdout.write('\x1b[2K')