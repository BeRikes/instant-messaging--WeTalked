from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from client_utils_gui.tk_register import Register
from client_utils_gui.tk_menu import Win as MenuWin
from client_utils_gui.tk_menu import MenuController

class LoginGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_input1 = self.__tk_input_m4mxk6z8(self)
        self.tk_input2 = self.__tk_input_m4mxk8uy(self)
        self.tk_button_m4mxm4tj = self.__tk_button_m4mxm4tj(self)
        self.tk_label_m4mxmymm = self.__tk_label_m4mxmymm(self)
        self.tk_label_m4mxmzx2 = self.__tk_label_m4mxmzx2(self)
        self.tk_label_m4mxq3jf = self.__tk_label_m4mxq3jf(self)
        self.tk_button_m4mxs7d1 = self.__tk_button_m4mxs7d1(self)

    def __win(self):
        self.title("we_talked")
        # 设置窗口大小、居中
        width = 460
        height = 300
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def __tk_input_m4mxk6z8(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=158, y=101, width=255, height=30)
        return ipt

    def __tk_input_m4mxk8uy(self, parent):
        ipt = Entry(parent, show='*')
        ipt.place(x=158, y=149, width=255, height=30)
        return ipt

    def __tk_button_m4mxm4tj(self, parent):
        btn = Button(parent, text="登录", takefocus=False, )
        btn.place(x=159, y=210, width=149, height=30)
        return btn

    def __tk_label_m4mxmymm(self, parent):
        label = Label(parent, text="用户名", anchor="center", )
        label.place(x=77, y=102, width=50, height=30)
        return label

    def __tk_label_m4mxmzx2(self, parent):
        label = Label(parent, text="密码", anchor="center", )
        label.place(x=77, y=149, width=50, height=30)
        return label

    def __tk_label_m4mxq3jf(self, parent):
        label = Label(parent, text="----登录----", anchor="center", )
        label.place(x=16, y=14, width=437, height=30)
        return label

    def __tk_button_m4mxs7d1(self, parent):
        btn = Button(parent, text="注册", takefocus=False, )
        btn.place(x=5, y=260, width=50, height=30)
        return btn


class Login(LoginGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.ctl.init(login=self)

    def __event_bind(self):
        self.tk_button_m4mxm4tj.bind('<Button-1>', self.ctl.submit)
        self.tk_button_m4mxs7d1.bind('<Button-1>', self.ctl.switch_login_reg)
        # 更快捷方便的登录
        self.tk_input1.bind('<Return>', lambda evt: self.tk_input2.focus_set())
        self.tk_input2.bind('<Return>', lambda evt: self.tk_button_m4mxm4tj.focus_set())
        self.tk_button_m4mxm4tj.bind('<Return>', self.ctl.submit)



class Controller:
    def __init__(self, s, buffer_size):
        self.login_cmd = 0
        self.s = s
        self.buffer_size = buffer_size
        self.login = None
        self.reg = None
        self.menu = None

    def init(self, login=None, reg=None):
        if login:
            self.login = login
        if reg:
            self.reg = reg

    def correct(self):
        if self.login_cmd == 1 and not self.reg.winfo_exists():
            self.login_cmd = 0

    def submit(self, evt):
        self.correct()
        print(f'now login cmd is {self.login_cmd}')
        user_name = self.login.tk_input1.get() if not self.login_cmd else self.reg.tk_input1.get()
        password = self.login.tk_input2.get() if not self.login_cmd else self.reg.tk_input2.get()
        if not user_name or not password:
            messagebox.showwarning("警告", "用户名和密码不能为空!")
            return
        msg = f"{self.login_cmd}\n{user_name}\n{password}"

        if self.login_cmd == 1:  # Register
            email = self.reg.tk_input3.get()
            phone_number = self.reg.tk_input4.get()
            if email == '':
                messagebox.showerror('错误', '邮箱不能为空')
                return
            msg += f'\n{email}'
            if phone_number != '':
                msg += f'\n{phone_number}'

        try:
            self.s.sendall(msg.encode())
            data = self.s.recv(self.buffer_size).decode()
            if data == 'yes':
                if self.login_cmd == 0:
                    messagebox.showinfo("成功", "登录成功, 密码正确")
                    self.login.withdraw()
                    self.menu = MenuWin(self.login, MenuController(self.s, self.buffer_size, user_name))
                    return
                elif self.login_cmd == 1:
                    messagebox.showinfo("成功", "账号注册成功")
                    self.switch_login_reg(None)  # Switch back to login mode
            elif data == 'no':
                messagebox.showerror("错误", "账号或密码错误!" if self.login_cmd == 0 else "请换一个用户名或者邮箱!")
            elif data == 'unknown':
                messagebox.showerror("错误", "该账号不存在，请先注册")
                response = messagebox.askyesno("提示", "是否注册?")
                if response:
                    self.switch_login_reg(None)
            else:
                messagebox.showerror("错误", "未知错误")
        except Exception as e:
            messagebox.showerror("错误", f"与服务器通信失败: {e}")

    def switch_login_reg(self, evt):
        self.correct()
        print(f'now login cmd is {self.login_cmd}')
        if self.login_cmd == 0:
            self.login_cmd = 1
            if self.reg is None or not self.reg.winfo_exists():
                register = Register(self.login, self)
            else:
                self.reg.deiconify()
        else:
            self.login_cmd = 0
            self.reg.withdraw()
            self.login.deiconify()


if __name__ == "__main__":
    s, buffer = 'a', 1024
    ctl = Controller(s, buffer)
    login = Login(ctl)
    login.mainloop()