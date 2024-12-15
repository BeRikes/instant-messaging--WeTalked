from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox


class WinGUI(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.__win()
        self.tk_button_button2 = self.__tk_button_button2(self)
        self.tk_button_button1 = self.__tk_button_button1(self)
        self.tk_input_input1 = self.__tk_input_input1(self)
        self.tk_input_input2 = self.__tk_input_input2(self)
        self.tk_label_label1 = self.__tk_label_label1(self)
        self.tk_label_label2 = self.__tk_label_label2(self)
        self.tk_button_seach_button = self.__tk_button_seach_button(self)
        self.rollFrame = self.__tk_rollFrame(self)

    def __win(self):
        self.title("we_talked")
        # 设置窗口大小、居中
        width = 420
        height = 388 # 194
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def __tk_button_button2(self, parent):
        btn = Button(parent, text="加群", takefocus=False)
        btn.place(x=104, y=0, width=100, height=30)
        return btn

    def __tk_button_button1(self, parent):
        btn = Button(parent, text="加好友", takefocus=False, )
        btn.place(x=0, y=0, width=100, height=30)
        return btn

    def __tk_input_input1(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=104, y=71, width=230, height=30)
        return ipt

    def __tk_input_input2(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=104, y=119, width=230, height=30)
        return ipt

    def __tk_label_label1(self, parent):
        label = Label(parent, text="用户名", anchor="center")
        label.place(x=33, y=71, width=50, height=30)
        return label

    def __tk_label_label2(self, parent):
        label = Label(parent, text="邮箱", anchor="center", )
        label.place(x=33, y=119, width=50, height=30)
        return label

    def __tk_button_seach_button(self, parent):
        btn = Button(parent, text="搜索", takefocus=False, )
        btn.place(x=358, y=54, width=34, height=126)
        return btn

    def __tk_rollFrame(self, parent):
        canvas = Canvas(parent)
        canvas.place(x=0, y=194, width=420, height=194)
        myscrollbar = Scrollbar(parent, orient="vertical", command=canvas.yview)  # 创建滚动条
        myscrollbar.place(x=400, y=194, height=194)
        canvas.configure(yscrollcommand=myscrollbar.set)
        rollFrame = Frame(canvas)
        canvas.create_window((0, 0), window=rollFrame, anchor='nw')  # 要用create_window才能跟随画布滚动
        rollFrame.bind("<Configure>",
                       lambda evt: canvas.configure(scrollregion=canvas.bbox("all"), width=420, height=194))
        return rollFrame

class Win(WinGUI):
    def __init__(self, root, controller):
        self.ctl = controller
        super().__init__(root)
        self.__event_bind()
        self.ctl.init(420, 194, self.tk_label_label1, self.tk_label_label2, self.tk_input_input1, self.tk_input_input2, self.rollFrame)

    def __event_bind(self):
        self.tk_button_button2.bind('<Button-1>', self.ctl.group_func)
        self.tk_button_button1.bind('<Button-1>', self.ctl.friend_func)
        self.tk_button_seach_button.bind('<Button-1>', self.ctl.search_fri_gro)


class add_ForG_Controller:
    def __init__(self, s, buffer_size, user_name):
        self.s = s
        self.buffer_size = buffer_size
        self.user_name = user_name
    def init(self, width, height, label1, label2, input1, input2, rollFrame):
        self.width, self.height = width, height
        self.label1, self.label2 = label1, label2
        self.input1, self.input2 = input1, input2
        self.rollFrame = rollFrame

    def group_func(self, evt):
        self.label1.config(text='群聊名称')
        if self.label2.winfo_ismapped():
            self.label2.place_forget()
            self.input2.place_forget()

    def friend_func(self, evt):
        self.label1.config(text='用户名')
        if not self.label2.winfo_ismapped():
            self.label2.place(x=33, y=119, width=50, height=30)
            self.input2.place(x=104, y=119, width=230, height=30)

    def search_fri_gro(self, evt):
        if self.label2.winfo_ismapped():
            # 加好友模式
            add_name, add_email = self.input1.get(), self.input2.get()
            if add_name == '' and add_email == '':
                messagebox.showerror('错误', '请输入内容')
                return
            if add_name == '': add_name = '$'
            if add_email == '': add_email = '$'
            send_msg = '4\n' + add_name + '\n' + add_email
            self.s.sendall(send_msg.encode())
            data = self.s.recv(self.buffer_size).decode()
            if data == '$':
                messagebox.showinfo('提示', '系统未找到此用户')
                return
            self.show_result(True, data)

    def show_result(self, friend: bool, content):
        for widget in self.rollFrame.winfo_children():     # 清楚之前的内容
            if isinstance(widget, Label):
                widget.destroy()
        self.rollFrame.update_idletasks()
        if friend:
            # 加好友信息显示
            label = Label(self.rollFrame, text='---------------------\n|' + content + '\n---------------------')
            label.grid(row=0, column=0)
            label.bind("<Double-Button-1>", lambda evt, info=content: self.add_friend(evt, info))
        else:
            content = content.split('\n')
            pass
            # for i, row in enumerate(content):

    def add_friend(self, evt, info):
        info = info.split('  ')
        another = info[0]
        response = messagebox.askyesno("提示", f"是否添加{another}为好友")
        if response:
            send_msg = '5\n' + self.user_name + '\n' + another
            self.s.sendall(send_msg.encode())
            data = self.s.recv(self.buffer_size).decode()
            if data == 'pending':
                messagebox.showinfo('成功', '好友请求已发送，等待对方同意')
                return
            else:
                messagebox.showerror('失败', '好友添加失败')
                return
        else:
            return






if __name__ == "__main__":
    root = Tk()
    win = Win(root, add_ForG_Controller('a', 1, 'han'))
    win.mainloop()