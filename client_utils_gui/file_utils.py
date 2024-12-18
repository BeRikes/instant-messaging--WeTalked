import os
from pathlib import Path
import threading
from tkinter import messagebox
import socket

def transmit_instant_files(self_ip, self_port, filenames, timeout):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        timer = threading.Timer(timeout, lambda s=s: timeout_close(s))
        timer.start()
        s.bind((self_ip, self_port - 1))
        s.listen()
        print(f"listening on {self_ip}:{self_port}")
        conn, addr = s.accept()
        timer.cancel()
        print('connected by', addr)
        messagebox.showinfo('启动', '启动文件传输')
        for filename in filenames:
            if not send_file(conn, filename):
                if not send_file(conn, filename):
                    messagebox.showerror('错误', f'{filename}文件传输失败')
                    return
        messagebox.showinfo('完成', '所有文件传输完毕')

def receive_instant_files(ip, port, base_dir, filenames, timeout):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        timer = threading.Timer(timeout, lambda s=s: timeout_close(s))
        timer.start()
        s.connect((ip, port))
        timer.cancel()
        print('\n'.join(filenames))
        messagebox.showinfo('启动', '启动文件传输')
        for file in filenames:
            file_path = os.path.join(base_dir, file)
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            if not receive_file(s, file_path):
                messagebox.showerror('错误', f'{file_path}文件传输失败')
                return
        messagebox.showinfo('完成', '所有文件传输完毕')

def timeout_close(s):
    s.close()
    messagebox.showerror('超时', '即使传输超时')

def receive_file(s, filename):
    with open(filename, 'wb') as file:
        while True:
            header = s.recv(4)       # 4字节定长头部，存放的是数据长度
            if not header:
                print("Connection closed by peer.")
                return False
            if header == b'\x00\x00\x00\x00':
                break
            data_len = int.from_bytes(header, 'big', signed=False)
            all = b''
            while data_len > 0:
                data = s.recv(data_len)
                all += data
                data_len -= len(data)
            file.write(all)
        s.sendall(b'yes')
    return True


def send_file(s, filename):
    # 打开文件以进行二进制读取
    with open(filename, 'rb') as file:
        while True:
            # 读取文件的块
            bytes_read = file.read(4096)
            if not bytes_read:
                break
            header = len(bytes_read).to_bytes(4, byteorder='big', signed=False)
            s.sendall(header + bytes_read)
    s.sendall(b'\x00\x00\x00\x00')   # 一个文件的传输结束标志
    response = s.recv(4)
    print(response)
    if response != b'yes':      # 接收方收完了此文件之后，才开始发送下一个文件
        print(f"Did not receive proper acknowledgment from receiver: {response}")
        return False
    return True


def get_file_list(startpath):
    abs_path_list, real_path_list, dir_list = [], [], []
    for root, dirs, files in os.walk(startpath):
        for file in files:
            abs_path_list.append(os.path.join(root, file))
            dir_list.append(os.path.dirname(abs_path_list[-1]))
    prefix = extract_longest_prefix(dir_list)
    for file in abs_path_list:
        real_path_list.append(str(Path(file).relative_to(Path(prefix))))
    return abs_path_list, real_path_list


def extract_longest_prefix(files):
    if not files:
        return ''
    shortest_str = min(files, key=len)  # 找到最短的字符串
    for i, char in enumerate(shortest_str):
        for other in files:
            if other[i] != char:
                return shortest_str[:i]
    return shortest_str