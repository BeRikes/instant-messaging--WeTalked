from tkinter import *
from tkinter.ttk import *


class file_trans_win(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self._win()
        self.progressbar = self.__tk_progressbar(self)
        self.rollFrame = self.__tk_rollFrame(self)
        self.label = self.__tk_label(self)

    def _win(self):
        self.title("we_talked文件传输")
        # 设置窗口大小、居中
        width = 364
        height = 285
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.iconbitmap('asset/we_talked.ico')
        self.resizable(width=False, height=False)

    def __tk_rollFrame(self, parent):
        canvas = Canvas(parent)
        canvas.place(x=0, y=0, width=349, height=199)
        yscrollbar = Scrollbar(parent, orient="vertical", command=canvas.yview)  # 创建滚动条
        yscrollbar.place(x=349, y=0, width=15, height=199)
        canvas.configure(yscrollcommand=yscrollbar.set)
        rollFrame = Frame(canvas)  # 在画布上创建frame
        canvas.create_window((0, 0), window=rollFrame, anchor='nw')  # 要用create_window才能跟随画布滚动
        rollFrame.bind("<Configure>", lambda evt: canvas.configure(scrollregion=canvas.bbox("all"), width=349, height=199))
        return rollFrame

    def __tk_progressbar(self, parent):
        progressbar = Progressbar(parent, orient=HORIZONTAL, )
        progressbar.place(x=51, y=219, width=168, height=30)
        return progressbar

    def __tk_label(self, parent):
        label = Label(parent, text="标签", anchor="center", )
        label.place(x=261, y=219, width=50, height=30)
        return label

class fileWin(file_trans_win):
    def __init__(self, root, max_file_num):
        super().__init__(root)
        self.progressbar['maximum'] = max_file_num
        self.progressbar['value'] = 0
        self.finished_label = Label(self, text='文件传输完成', anchor='center')
    def step(self, pace, name):
        self.progressbar['value'] += pace
        self.update()
        self.label.config(text=f'{self.progressbar["value"]}/{self.progressbar["maximum"]}')
        Label(self.rollFrame, text=name).pack(side='top')
        if self.progressbar['value'] == self.progressbar['maximum']:
            self.finished_label.place(x=182, y=252, width=80, height=30)


