import os.path
import re
import threading
import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import *

from client_utils_gui.file_utils import transmit_instant_files, receive_instant_files, get_file_list
from client_utils_gui.tk_talk_with_one import Controller as talkController
from client_utils_gui.tk_talk_with_one import Win as talkWin
from client_utils_gui.tk_talk_with_group import Controller as groupController
from client_utils_gui.tk_talk_with_group import Win as GroupWin
from client_utils_gui.tk_add_friend_or_group import add_ForG_Controller, Win as addWin
from client_utils_gui.tk_create_group import CreateGroupController, GroupCreater as CreateGroupWin


class WinGUI(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.__win()
        self.tk_button3 = self.__tk_button_m4ocpkbi(self)
        self.tk_button4 = self.__tk_button_m4ocpmgu(self)
        self.tk_button2 = self.__tk_button_m4ocvs0p(self)
        self.tk_button1 = self.__tk_button_m4ocvw71(self)
        self.tk_button5 = self.__tk_button_m4ocxrrl(self)
        self.tk_button6 = self.__tk_button_create_group(self)
        self.tk_label1 = self.__tk_label_m4p09wdw(self)
        self.tk_label2 = self.__tk_label_m4p0a79p(self)
        self.tk_rollFrame = self.__tk_rollFrame(self)
        self.trans_choice = self.__tk_file_func_choice(self)
    def __win(self):
        self.title("we_talked")
        # 设置窗口大小、居中
        width = 257
        height = 442
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.iconbitmap('asset/we_talked.ico')
        self.resizable(width=False, height=False)
    def __tk_button_m4ocpkbi(self,parent):
        btn = Button(parent, text="群聊", takefocus=False,)
        btn.place(x=130, y=86, width=60, height=42)
        return btn
    def __tk_button_m4ocpmgu(self,parent):
        btn = Button(parent, text="传输", takefocus=False,)
        btn.place(x=194, y=86, width=60, height=42)
        return btn
    def __tk_button_m4ocvs0p(self,parent):
        btn = Button(parent, text="联系人", takefocus=False,)
        btn.place(x=66, y=86, width=60, height=42)
        return btn
    def __tk_button_m4ocvw71(self,parent):
        btn = Button(parent, text="消息", takefocus=False,)
        btn.place(x=2, y=86, width=60, height=42)
        return btn
    def __tk_button_m4ocxrrl(self,parent):
        btn = Button(parent, text="加好友/群", takefocus=False,)
        btn.place(x=0, y=412, width=63, height=30)
        return btn

    def __tk_button_create_group(self,parent):
        btn = Button(parent, text="创建群聊", takefocus=False,)
        btn.place(x=68, y=412, width=63, height=30)
        return btn

    def __tk_label_m4p09wdw(self, parent):
        label = Label(parent, text="标签")
        label.place(x=20, y=30, width=138, height=30)
        return label

    def __tk_label_m4p0a79p(self, parent):
        label = Label(parent, text="标签")
        label.place(x=128, y=30, width=80, height=30)
        return label

    def __tk_rollFrame(self, parent):
        canvas = Canvas(parent)
        canvas.place(x=0, y=128, width=257, height=259)
        yscrollbar = Scrollbar(parent, orient="vertical", command=canvas.yview)  # 创建滚动条
        yscrollbar.place(x=240, y=128, height=259)
        xscrollbar = Scrollbar(parent, orient="horizontal", command=canvas.xview)
        xscrollbar.place(x=0, y=399, width=257, height=13)
        canvas.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        rollFrame = Frame(canvas)  # 在画布上创建frame
        canvas.create_window((0, 0), window=rollFrame, anchor='nw')  # 要用create_window才能跟随画布滚动
        rollFrame.bind("<Configure>", lambda evt: canvas.configure(scrollregion=canvas.bbox("all"), width=257, height=259))
        return rollFrame

    def __tk_file_func_choice(self, parent):
        v = StringVar(parent)
        dropdownmenu = OptionMenu(parent, v, "文件", "文件", "文件夹")
        dropdownmenu.place(x=187, y=61, width=75, height=25)
        return v


class Win(WinGUI):
    def __init__(self, root, controller):
        self.root = root
        self.ctl = controller
        super().__init__(root)
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self, self.tk_rollFrame, self.tk_label1, self.tk_label2, self.trans_choice, self.tk_button1,
                      self.tk_button2, self.tk_button3, self.tk_button4)
    def __event_bind(self):
        self.bind('<Destroy>', self.ctl.safe_exit)
        self.tk_button1.bind('<Button-1>', self.ctl.message)
        self.tk_button2.bind('<Button-1>', lambda evt: self.ctl.contact(evt, 2))
        self.tk_button3.bind('<Button-1>', self.ctl.group)
        self.tk_button4.bind('<Button-1>', lambda evt: self.ctl.contact(evt, 12))
        self.tk_button5.bind('<Button-1>', self.ctl.make_friend_or_group)
        self.tk_button6.bind('<Button-1>', self.ctl.create_group)

    def __style_config(self):
        style = Style()
        style.configure('TButton', foreground='black', background='SystemButtonFace')
        style.configure('Clicked.TButton', foreground='gray', background='black')


class MenuController:
    def __init__(self, s, buffer_size, user_name):
        self.s = s
        self.buffer_size = buffer_size
        self.user_name = user_name
        self.main_win = None
        self.last_state = 0

    def init(self, main_win, rollFrame, label1, label2, trans_choice, button1, button2, button3, button4):
        self.main_win = main_win
        self.rollFrame = rollFrame
        self.trans_choice = trans_choice
        self.all_button = [button1, button2, button3, button4]
        # for button in self.all_button:
        #     button.configure(style='TButton')
        label1.config(text=self.user_name)
        label2.config(text='welcome!')

    def config_button_color(self, new_state: int):
        self.all_button[self.last_state].configure(style='TButton')
        self.all_button[new_state].configure(style='Clicked.TButton')
        self.last_state = new_state

    def config_text_color(self, evt, frame, all_label: tuple, bd):
        frame.config(bg=bd)
        for label in all_label:
            label.config(bg=bd)

    def config_rollFrame(self, cmd, content):
        for widget in self.rollFrame.winfo_children():     # 清楚之前的内容
            if isinstance(widget, (tk.Label, tk.Frame)):
                widget.destroy()
        self.rollFrame.update_idletasks()

        content = content.split('\n')
        if cmd == 3:
            for i, row in enumerate(content):
                msg_id, another, content = row.split('$')
                f = tk.Frame(self.rollFrame)
                f.grid(row=i, column=0)
                label = tk.Label(f, text=another)
                label.pack(side='left')
                label2 = tk.Label(f, text=content)
                label2.pack(side='left')
                label.bind("<Double-Button-1>", lambda evt, info=row: self.message_talk(evt, info))
                label2.bind("<Double-Button-1>", lambda evt, info=row: self.message_talk(evt, info))
                f.bind('<Enter>', lambda evt, frame=f, all_label=(label, label2), bd='#DCDCDC': self.config_text_color(
                    evt, frame, all_label, bd))
                f.bind('<Leave>', lambda evt, frame=f, all_label=(label, label2), bd='SystemButtonFace': self.config_text_color(
                    evt, frame, all_label, bd))
        elif cmd == 2 or cmd == 12:
            for i, row in enumerate(content):
                name, isActive = row.split('$')
                f = tk.Frame(self.rollFrame)
                f.grid(row=i, column=0)
                label = tk.Label(f, text=name)
                label.pack(side='left')
                label2 = tk.Label(f, text='在线' if isActive == 'True' else '离线')
                label2.pack(side='left')
                f.bind('<Enter>', lambda evt, frame=f, all_label=(label, label2), bd='#DCDCDC': self.config_text_color(
                    evt, frame, all_label, bd))
                f.bind('<Leave>', lambda evt, frame=f, all_label=(label, label2), bd='SystemButtonFace': self.config_text_color(
                    evt, frame, all_label, bd))
                if cmd == 2:
                    label.bind("<Double-Button-1>", lambda evt, info=name: self.contact_talk(evt, info))
                    label2.bind("<Double-Button-1>", lambda evt, info=name: self.contact_talk(evt, info))
                else:
                    label.bind("<Double-Button-1>", lambda evt, another=name, act=isActive: self.req_file_instant_transmit(evt, another, act))
                    label2.bind("<Double-Button-1>", lambda evt, another=name, act=isActive: self.req_file_instant_transmit(evt, another, act))
        elif cmd == 17:
            for i, row in enumerate(content):
                print(row)
                group_name, group_id, message = row.split('$')
                f = tk.Frame(self.rollFrame)
                f.grid(row=i, column=0)
                label = tk.Label(f, text=f"{group_name}[{group_id}]")
                label.pack(side='left')
                if len(message) >= 25:
                    message = message[:23] + "……"
                label2 = tk.Label(f, text=message[:23])
                label2.pack(side='left')
                label.bind("<Double-Button-1>", lambda evt, info=row: self.group_talk(evt, info))
                label2.bind("<Double-Button-1>", lambda evt, info=row: self.group_talk(evt, info))
                f.bind('<Enter>', lambda evt, frame=f, all_label=(label, label2), bd='#DCDCDC': self.config_text_color(
                    evt, frame, all_label, bd))
                f.bind('<Leave>',
                       lambda evt, frame=f, all_label=(label, label2), bd='SystemButtonFace': self.config_text_color(
                           evt, frame, all_label, bd))
        else:
            for i, row in enumerate(content):
                label = tk.Label(self.rollFrame, text=row)
                label.grid(row=i, column=0, pady=5)

    def message(self, evt):
        self.config_button_color(0)
        send_msg = '3\n' + self.user_name
        self.s.sendall(send_msg.encode())
        data = self.s.recv(100 * self.buffer_size).decode()
        if data == '$':
            messagebox.showinfo('提示', '当前无任何消息')
            return
        else:
            self.config_rollFrame(3, data)

    def message_talk(self, evt, info):
        msg_id, another, content = info.split('$')
        if another == 'we_talked':      # 系统消息
            if content.find('好友') != -1:
                apply_friend = content[:-6]
                send_msg = '10\n' + self.user_name + '\n' + apply_friend + '\n' + msg_id
                self.s.sendall(send_msg.encode())
                data = self.s.recv(self.buffer_size).decode()
                if data == 'yes':
                    messagebox.showinfo("成功", f"{apply_friend}现在是你的好友了")
                    self.message(None)
                    return
                else:
                    messagebox.showerror("错误", f"操作失败，失败原因:{data}")
                    return
            elif content.find('文件') != -1:
                idx = content.find('请求文件传输')
                files = content[:idx]
                send_msg = '13\n' + self.user_name + '\n' + files + '\n' + msg_id
                self.s.sendall(send_msg.encode())
                data = self.s.recv(self.buffer_size).decode()
                if data == '-1':
                    messagebox.showerror('错误', '对方不在线，请等到下次传输')
                    return
                if data == '0':
                    messagebox.showerror('错误', '未找到此信息')
                    return
                if data == '1':
                    messagebox.showerror('错误', '删除消息时，出现错误，请重试')
                    return
                else:
                    save_dir = filedialog.askdirectory(initialdir='/', title='选择文件传输时,存放的目录')
                    ip, port = data.split('\n')
                    trans_thread = threading.Thread(target=receive_instant_files, args=(self.main_win, ip, int(port), save_dir, content[idx + 6:], 5),
                                                    daemon=True)
                    trans_thread.start()
                    self.message(None)
                    return
            elif content.find('群聊'):
                pattern = r'\[(.*?)\]'
                last_invite_pos = content.rfind("邀请")
                last_request_pos = content.rfind("请求")
                last_pos = max(last_invite_pos, last_request_pos)
                group_id = re.findall(pattern, content)
                receiver = content[:last_pos]
                send_msg = '15\n' + self.user_name + '\n' + receiver + '\n' + group_id[-1] + '\n' + msg_id
                self.s.sendall(send_msg.encode())
                data = self.s.recv(self.buffer_size).decode()
                if data == 'accept':
                    messagebox.showinfo("成功", f"已通过群聊申请")
                    self.message(None)
                    return
                else:
                    messagebox.showerror("错误", f"操作失败，失败原因:{data}")
                    return
        else:
            new_win = talkWin(self.main_win, talkController(self.s, self.buffer_size, self.user_name, another))


    def contact(self, evt, cmd):
        self.config_button_color(1 if cmd == 2 else 3)
        send_msg = '2\n' + self.user_name
        self.s.sendall(send_msg.encode())  # 获取用户所有好友信息，并打印输出
        contacts = self.s.recv(100 * self.buffer_size).decode()
        if contacts == '$':
            messagebox.showinfo('提示', '无联系人，请先去添加好友')
            return
        else:
            self.config_rollFrame(cmd, contacts)

    def contact_talk(self, evt, info):
        new_win = talkWin(self.main_win, talkController(self.s, self.buffer_size, self.user_name, info))

    def group(self, evt):
        self.config_button_color(2)
        send_msg = '17\n' + self.user_name
        self.s.sendall(send_msg.encode())
        groups = self.s.recv(100 * self.buffer_size).decode()
        if groups == '$':
            messagebox.showinfo('提示', '当前未加入群聊')
            return
        else:
            self.config_rollFrame(17, groups)
        return

    def group_talk(self, evt, info):
        group_name, group_id, message = info.split('$')
        new_win = GroupWin(self.main_win, groupController(self.s, self.buffer_size, self.user_name, group_name, group_id))

    def req_file_instant_transmit(self, evt, another, act):
        if act == 'False':
            messagebox.showerror('错误', '对方不在线，无法传输')
            return
        choice = self.trans_choice.get()
        if choice == '文件':
            files = filedialog.askopenfilenames(initialdir='/', title='选择传输的文件')
            if len(files) == 0:
                return
            files_msg = [os.path.basename(file) for file in files]
        else:   # choice == '文件夹'
            filedir = filedialog.askdirectory(initialdir='/', title='选择传输的文件夹')
            files, real_path = get_file_list(filedir)
            if len(files) == 0:
                messagebox.showerror('失败', '用户取消选择或者该文件夹为空')
                return
            base_dir = os.path.basename(filedir)
            files_msg = [os.path.join(base_dir, file) for file in real_path]
        files_msg = '@'.join(files_msg).rstrip('@')   # 保留字符(@,$,\n，即用户发送内容之中不能包含这几个字符)
        if len(files_msg) > self.buffer_size * 100:
            messagebox.showerror('失败', '所选文件过于庞大，请选择小一点的文件/文件夹')
            return
        send_msg = '12\n' + self.user_name + '\n' + another + '\n' + files_msg
        self.s.sendall(send_msg.encode())
        data = self.s.recv(self.buffer_size).decode()
        if data == 'pending':
            messagebox.showinfo('成功', '文件传输请求已发送，等待对方确认')
            host, port = self.s.getsockname()
            trans_thread = threading.Thread(target=transmit_instant_files, args=(self.main_win, host, port, files, 25), daemon=True)
            trans_thread.start()
        else:
            messagebox.showinfo('失败', '服务器拒绝你的文件传输请求')

    def make_friend_or_group(self, evt):
        new_win = addWin(self.main_win, add_ForG_Controller(self.s, self.buffer_size, self.user_name))

    def create_group(self, evt):
        new_win = CreateGroupWin(self.main_win, CreateGroupController(self.s, self.buffer_size, self.user_name))

    def safe_exit(self, evt):
        if evt.widget == self.main_win:
            send_msg = '11\n' + self.user_name
            self.s.sendall(send_msg.encode())
            print(self.s.recv(8), 'to exit')
            self.main_win.root.quit()

