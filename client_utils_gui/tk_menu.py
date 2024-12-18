import os.path
import threading
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import *

from client_utils_gui.file_utils import transmit_instant_files, receive_instant_files, get_file_list
from client_utils_gui.tk_talk_with_one import Controller as talkController
from client_utils_gui.tk_talk_with_one import Win as talkWin
from client_utils_gui.tk_add_friend_or_group import add_ForG_Controller, Win as addWin

class WinGUI(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.__win()
        self.tk_button3 = self.__tk_button_m4ocpkbi(self)
        self.tk_button4 = self.__tk_button_m4ocpmgu(self)
        self.tk_button2 = self.__tk_button_m4ocvs0p(self)
        self.tk_button1 = self.__tk_button_m4ocvw71(self)
        self.tk_button5 = self.__tk_button_m4ocxrrl(self)
        self.tk_label1 = self.__tk_label_m4p09wdw(self)
        self.tk_label2 = self.__tk_label_m4p0a79p(self)
        self.tk_rollFrame = self.__tk_rollFrame(self)
        self.trans_choice = self.__tk_file_func_choice(self)
    def __win(self):
        self.title("we_talked")
        # 设置窗口大小、居中
        width = 257
        height = 426
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

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
        btn.place(x=0, y=396, width=63, height=30)
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
        myscrollbar = Scrollbar(parent, orient="vertical", command=canvas.yview)  # 创建滚动条
        myscrollbar.place(x=240, y=128, height=259)
        canvas.configure(yscrollcommand=myscrollbar.set)
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
        self.ctl.init(self, self.tk_rollFrame, self.tk_label1, self.tk_label2, self.trans_choice)
    def __event_bind(self):
        self.bind('<Destroy>', self.ctl.safe_exit)
        self.tk_button1.bind('<Button-1>', self.ctl.message)
        self.tk_button2.bind('<Button-1>', lambda evt: self.ctl.contact(evt, 2))
        self.tk_button3.bind('<Button-1>', self.ctl.group)
        self.tk_button4.bind('<Button-1>', lambda evt: self.ctl.contact(evt, 12))
        self.tk_button5.bind('<Button-1>', self.ctl.make_friend_or_group)

    def safe_destroy(self, evt):
        if evt.widget == self:
            self.root.quit()

class MenuController:
    def __init__(self, s, buffer_size, user_name):
        self.s = s
        self.buffer_size = buffer_size
        self.user_name = user_name
        self.main_win = None

    def init(self, main_win, rollFrame, label1, label2, trans_choice):
        self.main_win = main_win
        self.rollFrame = rollFrame
        self.trans_choice = trans_choice
        label1.config(text=self.user_name)
        label2.config(text='welcome!')

    def config_rollFrame(self, cmd, content):
        for widget in self.rollFrame.winfo_children():     # 清楚之前的内容
            if isinstance(widget, (Label, Frame)):
                widget.destroy()
        self.rollFrame.update_idletasks()

        content = content.split('\n')
        if cmd == 3:
            for i, row in enumerate(content):
                msg_id, another, content = row.split('$')
                f = Frame(self.rollFrame)
                label = Label(f, text=another)
                label.grid(row=0, column=0, pady=5)
                label.bind("<Double-Button-1>", lambda evt, info=row: self.message_talk(evt, info))
                label2 = Label(f, text=content)
                label2.grid(row=0, column=1, pady=5)
                label2.bind("<Double-Button-1>", lambda evt, info=row: self.message_talk(evt, info))
                f.grid(row=i, column=0)
        elif cmd == 2 or cmd == 12:
            for i, row in enumerate(content):
                name, isActive = row.split('$')
                label = Label(self.rollFrame, text=name)
                label.grid(row=i, column=0, pady=5)
                label2 = Label(self.rollFrame, text='在线' if isActive == 'True' else '离线')
                label2.grid(row=i, column=1, pady=5)
                if cmd == 2:
                    label.bind("<Double-Button-1>", lambda evt, info=name: self.contact_talk(evt, info))
                    label2.bind("<Double-Button-1>", lambda evt, info=name: self.contact_talk(evt, info))
                else:
                    label.bind("<Double-Button-1>", lambda evt, another=name, act=isActive: self.req_file_instant_transmit(evt, another, act))
                    label2.bind("<Double-Button-1>", lambda evt, another=name, act=isActive: self.req_file_instant_transmit(evt, another, act))
        else:
            for i, row in enumerate(content):
                label = Label(self.rollFrame, text=row)
                label.grid(row=i, column=0, pady=5)
            # 貌似这个bind只对最后一个Label有效
            # label.bind("<Enter>", lambda evt: label.config(background='#DCDCDC'))
            # label.bind("<Leave>", lambda evt: label.config(background='SystemButtonFace'))

    def message(self, evt):
        send_msg = '3\n' + self.user_name
        self.s.sendall(send_msg.encode())
        data = self.s.recv(self.buffer_size).decode()
        if data == '$':
            messagebox.showinfo('提示', '当前无任何消息')
            return
        else:
            self.config_rollFrame(3, data)

    def message_talk(self, evt, info):
        msg_id, another, content = info.split('$')
        if another == 'we_talked':      # 系统消息
            if content.find('好友') != -1:
                another = content[:-6]
                send_msg = '10\n' + self.user_name + '\n' + another + '\n' + msg_id
                self.s.sendall(send_msg.encode())
                data2 = self.s.recv(self.buffer_size).decode()
                if data2 == 'yes':
                    messagebox.showinfo("成功", f"{another}现在是你的好友了")
                    self.message(None)
                else:
                    messagebox.showerror("错误", f"操作失败，失败原因:{data2}")
            elif content.find('文件') != -1:
                idx = content.find('请求文件传输')
                another = content[:idx]
                send_msg = '13\n' + self.user_name + '\n' + another + '\n' + msg_id
                self.s.sendall(send_msg.encode())
                data = self.s.recv(self.buffer_size).decode()
                if data == '0':
                    messagebox.showerror('错误', '未找到此信息')
                elif data == '1':
                    messagebox.showerror('错误', '删除消息时，出现错误，请重试')
                else:
                    ip, port = data.split('\n')
                    filenames = content[idx + 6:].split('@')
                    save_dir = filedialog.askdirectory(initialdir='/', title='选择文件传输时,存放的目录')
                    trans_thread = threading.Thread(target=receive_instant_files, args=(ip, int(port), save_dir, filenames, 5),
                                                    daemon=True)
                    trans_thread.start()
                    self.message(None)
        else:
            new_win = talkWin(self.main_win, talkController(self.s, self.buffer_size, self.user_name, another))


    def contact(self, evt, cmd):
        send_msg = '2\n' + self.user_name
        self.s.sendall(send_msg.encode())  # 获取用户所有好友信息，并打印输出
        contacts = self.s.recv(self.buffer_size).decode()
        if contacts == '$':
            messagebox.showinfo('提示', '无联系人，请先去添加好友')
            return
        else:
            self.config_rollFrame(cmd, contacts)

    def contact_talk(self, evt, info):
        new_win = talkWin(self.main_win, talkController(self.s, self.buffer_size, self.user_name, info))

    def group(self, evt):
        messagebox.showwarning('警告', '此功能尚未实现')

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
                return
            base_dir = os.path.basename(filedir)
            files_msg = [os.path.join(base_dir, file) for file in real_path]
        files_msg = '@'.join(files_msg).rstrip('@')   # 保留字符(@,$,\n，即用户发送内容之中不能包含这几个字符)
        send_msg = '12\n' + self.user_name + '\n' + another + '\n' + files_msg
        self.s.sendall(send_msg.encode())
        data = self.s.recv(self.buffer_size).decode()
        if data == 'pending':
            messagebox.showinfo('成功', '文件传输请求已发送，等待对方确认')
            host, port = self.s.getsockname()
            trans_thread = threading.Thread(target=transmit_instant_files, args=(host, port, files, 500), daemon=True)
            trans_thread.start()
        else:
            messagebox.showinfo('失败', '服务器拒绝你的文件传输请求')




    def make_friend_or_group(self, evt):
        new_win = addWin(self.main_win, add_ForG_Controller(self.s, self.buffer_size, self.user_name))

    def safe_exit(self, evt):
        if evt.widget == self.main_win:
            send_msg = '11\n' + self.user_name
            self.s.sendall(send_msg.encode())
            print(self.s.recv(8), 'to exit')
            self.main_win.root.quit()





if __name__ == "__main__":
    win = Win(MenuController('a', 1, 'han', 'h@yycom'))
    win.mainloop()