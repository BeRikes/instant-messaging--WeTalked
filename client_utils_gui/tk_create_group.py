from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox


class CreateGroupGUI(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.__win()
        self.tk_input1 = self.__tk_input1(self)
        self.tk_text1 = self.__tk_text1(self)
        self.tk_button_create = self.__tk_button_create(self)
        self.tk_label_group_name = self.__tk_label_group_name(self)
        self.tk_label_group_introduce = self.__tk_label_group_introduce(self)
        self.tk_label_index = self.__tk_label_index(self)

    def __win(self):
        self.title("we-talked： 创建群聊")
        # 设置窗口大小、居中
        width = 468
        height = 376
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def __tk_input1(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=110, y=66, width=295, height=30)
        return ipt

    def __tk_text1(self, parent):
        ipt = Text(parent, wrap=WORD)
        ipt.place(x=110, y=121, width=295, height=130)
        return ipt

    def __tk_button_create(self, parent):
        btn = Button(parent, text="创建群聊", takefocus=False, )
        btn.place(x=120, y=287, width=232, height=30)
        return btn

    def __tk_label_group_name(self, parent):
        label = Label(parent, text="群聊名称", anchor="center", )
        label.place(x=40, y=66, width=60, height=30)
        return label

    def __tk_label_group_introduce(self, parent):
        label = Label(parent, text="群聊介绍", anchor="center", )
        label.place(x=40, y=121, width=60, height=30)
        return label

    def __tk_label_index(self, parent):
        label = Label(parent, text="----创建群聊----", anchor="center", )
        label.place(x=16, y=14, width=437, height=30)
        return label


class GroupCreater(CreateGroupGUI):
    def __init__(self, root, controller):
        self.ctl = controller
        super().__init__(root)
        self.__event_bind()
        self.ctl.init(468, 376, self.tk_label_index, self.tk_label_group_name, self.tk_label_group_introduce, self.tk_input1, self.tk_text1)

    def __event_bind(self):
        self.tk_button_create.bind('<Button-1>', self.ctl.group_submit)


class CreateGroupController:
    def __init__(self, s, buffer_size, user_name):
        self.s = s
        self.buffer_size = buffer_size
        self.user_name = user_name

    def init(self, width, height, index, label1, label2, input1, text1):
        self.width, self.height = width, height
        self.index = index
        self.label1, self.label2 = label1, label2
        self.input1, self.text1 = input1, text1

    def group_submit(self, evt):
        group_name, group_introduce = self.input1.get(), self.text1.get("1.0", END + "-1c")
        if group_name == '':
            messagebox.showerror('错误', '请输入群聊名称')
            return
        if group_introduce == '':
            group_introduce = '此群聊暂无介绍'

        send_msg = '14\n' + self.user_name + '\n' + group_name + '\n' + group_introduce + '\n'
        self.s.sendall(send_msg.encode())
        data = self.s.recv(self.buffer_size).decode()

        if data == 'success':
            messagebox.showinfo("成功", "群聊创建成功")
        elif data == 'invalid':
            messagebox.showerror("错误", "群聊创建失败：非法群聊名称")
        else:
            messagebox.showerror("错误", "未知错误")



