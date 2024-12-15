from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

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
        btn = Button(parent, text="文件", takefocus=False,)
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
        label = Label(parent, text="标签", anchor="center", )
        label.place(x=0, y=30, width=50, height=30)
        return label

    def __tk_label_m4p0a79p(self, parent):
        label = Label(parent, text="标签", anchor="center", )
        label.place(x=77, y=30, width=134, height=30)
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


class Win(WinGUI):
    def __init__(self, root, controller):
        self.root = root
        self.ctl = controller
        super().__init__(root)
        self.__event_bind()
        self.ctl.init(self, self.tk_rollFrame, self.tk_label1, self.tk_label2)
    def __event_bind(self):
        self.bind('<Destroy>', self.safe_destroy)
        self.tk_button1.bind('<Button-1>', self.ctl.message)
        self.tk_button2.bind('<Button-1>', self.ctl.contact)
        self.tk_button3.bind('<Button-1>', self.ctl.group)
        self.tk_button4.bind('<Button-1>', self.ctl.file_function)
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

    def init(self, main_win, rollFrame, label1, label2):
        self.main_win = main_win
        self.rollFrame = rollFrame
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
        elif cmd == 2:
            for i, row in enumerate(content):
                label = Label(self.rollFrame, text=row)
                label.grid(row=i, column=0, pady=5)
                label.bind("<Double-Button-1>", lambda evt, info=row: self.contact_talk(evt, info))
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
            self.config_rollFrame(3, '什么都没有~~')
        else:
            self.config_rollFrame(3, data)

    def message_talk(self, evt, info):
        msg_id, another, content = info.split('$')
        if another == 'we_talked':      # 系统消息
            if content.find('添加好友') != -1:
                another = content[:-6]
                send_msg = '10\n' + self.user_name + '\n' + another + '\n' + msg_id
                self.s.sendall(send_msg.encode())
                data2 = self.s.recv(self.buffer_size).decode()
                if data2 == 'yes':
                    messagebox.showinfo("成功", f"{another}现在是你的好友了")
                else:
                    messagebox.showerror("错误", f"操作失败，失败原因:{data2}")
        else:
            new_win = talkWin(self.main_win, talkController(self.s, self.buffer_size, self.user_name, another))


    def contact(self, evt):
        send_msg = '2\n' + self.user_name
        self.s.sendall(send_msg.encode())  # 获取用户所有好友信息，并打印输出
        contacts = self.s.recv(self.buffer_size).decode()
        self.config_rollFrame(2, contacts)

    def contact_talk(self, evt, info):
        new_win = talkWin(self.main_win, talkController(self.s, self.buffer_size, self.user_name, info))

    def group(self, evt):
        messagebox.showwarning('警告', '此功能尚未实现')

    def file_function(self, evt):
        messagebox.showwarning('警告', '此功能尚未实现')

    def make_friend_or_group(self, evt):
        new_win = addWin(self.main_win, add_ForG_Controller(self.s, self.buffer_size, self.user_name))


    def tk_exit(self, evt):
        print('exit')


# def talk_with_another_new_win(parent, s, buffer_size, user_name, another_name):
#     talk_ctl = talkController(s, buffer_size, user_name, another_name)
#     talk_win = talkWin(parent, talk_ctl)


if __name__ == "__main__":
    win = Win(MenuController('a', 1, 'han', 'h@yycom'))
    win.mainloop()