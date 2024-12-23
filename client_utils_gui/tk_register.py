from tkinter import *
from tkinter.ttk import *


class RegisterGUI(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.__win()
        self.tk_input1 = self.__tk_input_m4mxk6z8(self)
        self.tk_input2 = self.__tk_input_m4mxk8uy(self)
        self.tk_button_m4mxm4tj = self.__tk_button_m4mxm4tj(self)
        self.tk_label_m4mxmymm = self.__tk_label_m4mxmymm(self)
        self.tk_label_m4mxmzx2 = self.__tk_label_m4mxmzx2(self)
        self.tk_label_m4mxq3jf = self.__tk_label_m4mxq3jf(self)
        self.tk_button_m4mxs7d1 = self.__tk_button_m4mxs7d1(self)
        self.tk_label_m4myc7ru = self.__tk_label_m4myc7ru(self)
        self.tk_input3 = self.__tk_input_m4mycbqs(self)
        self.tk_label_m4mycnrj = self.__tk_label_m4mycnrj(self)
        self.tk_input4 = self.__tk_input_m4mycpko(self)

    def __win(self):
        self.title("we-talked 注册")
        # 设置窗口大小、居中
        width = 468
        height = 376
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.iconbitmap('asset/we_talked.ico')
        self.resizable(width=False, height=False)

    def __tk_input_m4mxk6z8(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=150, y=66, width=255, height=30)
        return ipt

    def __tk_input_m4mxk8uy(self, parent):
        ipt = Entry(parent)
        ipt.place(x=150, y=121, width=255, height=30)
        return ipt

    def __tk_button_m4mxm4tj(self, parent):
        btn = Button(parent, text="注册", takefocus=False, )
        btn.place(x=120, y=287, width=232, height=30)
        return btn

    def __tk_label_m4mxmymm(self, parent):
        label = Label(parent, text="用户名", anchor="center", )
        label.place(x=75, y=66, width=50, height=30)
        return label

    def __tk_label_m4mxmzx2(self, parent):
        label = Label(parent, text="密码", anchor="center", )
        label.place(x=75, y=121, width=50, height=30)
        return label

    def __tk_label_m4mxq3jf(self, parent):
        label = Label(parent, text="----注册----", anchor="center", )
        label.place(x=16, y=14, width=437, height=30)
        return label

    def __tk_button_m4mxs7d1(self, parent):
        btn = Button(parent, text="登录", takefocus=False, )
        btn.place(x=7, y=336, width=50, height=30)
        return btn

    def __tk_label_m4myc7ru(self, parent):
        label = Label(parent, text="邮箱", anchor="center", )
        label.place(x=75, y=173, width=50, height=30)
        return label

    def __tk_input_m4mycbqs(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=150, y=173, width=256, height=30)
        return ipt

    def __tk_label_m4mycnrj(self, parent):
        label = Label(parent, text="电话号", anchor="center", )
        label.place(x=75, y=227, width=50, height=30)
        return label

    def __tk_input_m4mycpko(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=150, y=227, width=257, height=30)
        return ipt


class Register(RegisterGUI):
    def __init__(self, root, controller):
        self.ctl = controller
        super().__init__(root)
        self.__event_bind()
        self.ctl.init(reg=self)

    def __event_bind(self):
        self.tk_button_m4mxm4tj.bind('<Button-1>', self.ctl.submit)
        self.tk_button_m4mxs7d1.bind('<Button-1>', self.ctl.switch_login_reg)