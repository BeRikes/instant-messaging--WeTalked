import threading
import time
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *


class WinGUI(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.__win()
        self.tk_text_history_msg = self.__tk_text_history_msg(self)
        self.tk_text_talk_with = self.__tk_text_talk_with(self)
        self.tk_text_input_msg = self.__tk_text_input_msg(self)
        self.tk_send_msg_button = self.__tk_send_msg_button(self)
        self.tk_button_image_button = self.__tk_button_image_button(self)
        self.tk_button_file_button = self.__tk_button_file_button(self)
        self.tk_button_add_member = self.__tk_button_add_member(self)

    def __win(self):
        self.title("we_talked")
        # 设置窗口大小、居中
        width = 582
        height = 381
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def scrollbar_autohide(self, vbar, hbar, widget):
        """自动隐藏滚动条"""

        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)

        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)

        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def __tk_text_history_msg(self, parent):
        text = Text(parent)
        text.place(x=13, y=36, width=544, height=208)
        self.create_bar(parent, text, True, False, 13, 36, 544, 208, 582, 381)
        return text

    def __tk_text_talk_with(self, parent):
        text = Text(parent)
        text.place(x=156, y=0, width=260, height=35)
        return text

    def __tk_text_input_msg(self, parent):
        text = Text(parent)
        text.place(x=13, y=276, width=543, height=72)
        self.create_bar(parent, text, True, False, 13, 276, 543, 72, 582, 381)
        return text

    def __tk_send_msg_button(self, parent):
        btn = Button(parent, text="发送", takefocus=False, )
        btn.place(x=207, y=350, width=169, height=30)
        return btn

    def __tk_button_image_button(self, parent):
        btn = Button(parent, text="图片", takefocus=False, )
        btn.place(x=13, y=245, width=50, height=30)
        return btn

    def __tk_button_file_button(self, parent):
        btn = Button(parent, text="文件", takefocus=False, )
        btn.place(x=64, y=245, width=50, height=30)
        return btn

    def __tk_button_add_member(self, parent):
        btn = Button(parent, text="邀请新成员", takefocus=False, )
        btn.place(x=467, y=245, width=90, height=30)
        return btn


class Win(WinGUI):
    def __init__(self, root, controller):
        self.ctl = controller
        super().__init__(root)
        self.__event_bind()
        self.ctl.init(self.tk_text_input_msg, self.tk_text_history_msg, self.tk_text_talk_with)
        self.stop_event = threading.Event()
        self.convers_thread = threading.Thread(target=self.ctl.insert_group_msg, args=(self.stop_event,))
        self.convers_thread.start()
        self.bind('<Destroy>', lambda evt: self.stop_event.set())
    def __event_bind(self):
        self.tk_text_input_msg.bind('<Return>', self.ctl.message_to_group)
        # self.tk_text_input_msg.bind("<Shift-Return>", self.ctl.input_an_enter)
        self.tk_send_msg_button.bind('<Button-1>', self.ctl.message_to_group)
        self.tk_button_image_button.bind('<Button-1>', self.ctl.image_send_to)
        self.tk_button_file_button.bind('<Button-1>', self.ctl.file_send_to)
        self.tk_button_add_member.bind('<Button-1>', self.ctl.invite_new_member)


class Controller:
    def __init__(self, s, buffer_size, user_name, group_name, group_id):
        self.s = s
        self.buffer = buffer_size
        self.group_name = group_name
        self.group_id = group_id
        self.user_name = user_name
        self.after = '0'
        self.pre_time = '2020-01-01 00:00:00'
        self.socket_lock = threading.Lock()

    def init(self, input_msg, his_msg, top_info):
        self.input_msg = input_msg
        self.his_msg = his_msg
        self.top_info = top_info
        self.top_info.insert(END, '\t-----we_talked-----\n')
        self.top_info.tag_configure("center", justify='center')
        # 插入文本并应用居中对齐的标签
        self.top_info.insert(END, self.group_name, "center")
        self.top_info.configure(state=DISABLED)

    def insert_group_msg(self, stop_event):
        while not stop_event.is_set():
            msg = '18\n' + self.user_name + '\n' + self.group_id + '\n' + self.after + '\n' + self.pre_time
            self.s.sendall(msg.encode())
            with self.socket_lock:
                data = self.s.recv(4 * self.buffer if self.after == '0' else self.buffer)
            self.after, content, self.pre_time = data.decode().split('$')
            print(content)
            if content != 'no news':
                self.his_msg.configure(state=NORMAL)
                self.his_msg.insert(END, content + '\n')
                self.his_msg.see(END)  # 自动滚动到底部
                self.his_msg.configure(state=DISABLED)
            time.sleep(2)

    def message_to_group(self, evt):
        """Enter快捷键或者点击发送按键发送消息,同时清空输入框"""
        input = self.input_msg.get("1.0", END + "-1c")
        self.input_msg.delete("1.0", END)
        if not input:
            messagebox.showwarning("警告", "发送内容为空")
            return 'break'
        send_msg = '19\n' + self.user_name + '\n' + self.group_id + '\n' + input.replace("\n", "")
        self.s.sendall(send_msg.encode())
        with self.socket_lock:
            data = self.s.recv(self.buffer).decode()
        if data == 'no':
            messagebox.showwarning("警告", '此条消息发送失败')
        return 'break'     # 去除残留回车键

    def image_send_to(self, evt):
        print("<Button-1>事件未处理:", evt)
    def file_send_to(self, evt):
        print("<Button-1>事件未处理:", evt)

    def invite_new_member(self, evt):
        print("")