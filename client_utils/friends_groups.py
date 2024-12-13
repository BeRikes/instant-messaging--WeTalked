import os

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
        else:
            print('无此功能，重新输入')


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
                try:
                    idx = int(input('选择一个群聊: (禁止选不存在)')) - 1
                    group_id = data[idx][:content_idx[idx] - 1]
                except Exception:
                    continue
                send_msg = '8\n' + group_id + '\n' + user_id
                s.sendall(send_msg.encode())
                join_in_result = s.recv(buffer_size).decode()
                if join_in_result == 'yes':
                    print("群聊加入成功")
                elif join_in_result == 'no':
                    print('群聊加入失败')
                elif join_in_result == 'pending':     # 服务器先给群主发送{用户加群请求}的消息，群主何时同意，用户何时能加入群聊
                    print('需要群主审核，等待后续通知')
                break
