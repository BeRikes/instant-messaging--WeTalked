import threading
import time
import os


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
            send_msg = input()
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


def conversation_content_update(stop_event, s, buffer_size, user_name, another):
    after = '2020-01-01 00:00:00'
    while not stop_event.is_set():
        msg = '9\n' + user_name + '\n' + another + '\n' + after
        s.sendall(msg.encode())
        data = s.recv(buffer_size).decode()
        gap_idx = data.find('\n')
        after = data[:gap_idx]
        if len(data[gap_idx + 1:]) != 7 or data[gap_idx + 1:] != 'no news':
            print(data[gap_idx + 1:])
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
        print('-------------------------------')
        for i, item in enumerate(data):
            print('|', i + 1, item.replace('$', '  ') + '\n-------------------------------')
        # 决定是否同意系统通知(如we_talked: xxx请求添加好友), 或者与一个好友开始通讯
        choice = int(input("选择一个会话，开始通讯，输入-1返回菜单"))
        while choice < -1 or choice > len(data):
            choice = int(input("请重新输入，输入-1返回菜单"))
        if choice == -1:
            return
        another, content = data[choice - 1].split('$')
        if another == 'we_talked':
            another = content[:-6]
            if content.find('添加好友') != -1:
                send_msg = '10\n' + user_id + '\n' + another
                s.sendall(send_msg.encode())
                data2 = s.recv(buffer).decode()
                if data2 == 'yes':
                    print(another + '现在是你的好友了!')
                else:
                    print('操作失败，失败原因:', data2)
        else:
            talk_with_another(s, buffer, user_id, another)