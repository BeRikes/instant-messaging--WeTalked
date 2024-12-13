import time


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
        if user_id == '' or password == '': continue
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
                time.sleep(2)
                return user_id
            elif login_cmd == '1':
                print('账号注册成功')
                time.sleep(2)
                login_cmd = '0'
                data = 'no'
        elif data == 'no':
            if login_cmd == '0': print('账号或密码错误!')
            else: print('请换一个用户名或者邮箱!')
        elif data == 'unknown':
            print("该账号不存在，请先注册")
            if input("是否注册<yes/no>") == 'yes':
                login_cmd = '1'