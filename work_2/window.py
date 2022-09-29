from tkinter import *
import sys
sys.path.append("./")
from bitter_work import *


def bitter_gen_work():  # 提供给按钮链接 生成表达式并计算表达式的值 后存放进指定文件

    expression_num = expression_num_input.get()
    max_num = max_num_input.get()
    expression_num = int(expression_num)
    max_num = int(max_num)
    tip = gen_work(expression_num, max_num)
    message.insert(END, "\n" + tip + "\n")


def bitter_check_work():  # 提供给按钮链接 检查答案文件与测试文件的差别 统计正确和错误情况

    answer_path = answer_path_input.get()
    test_path = test_path_input.get()
    tip = check_work(answer_path, test_path)
    message.insert(END, "\n" + tip + "\n")


if __name__ == '__main__':  # 定义图形界面

    root = Tk()
    root.geometry('550x330')
    root.title('bitter的四则运算生成/检查器')

    explain = Label(root, text='请输入四个参数 分别为"expression_num" "max_num" "answer_path" "test_path"')
    explain.place(relx=0.075, rely=0.05, relwidth=0.85, relheight=0.1)
    expression_num_input = Entry(root)
    expression_num_input.place(relx=0.1, rely=0.2, relwidth=0.3, relheight=0.1)
    max_num_input = Entry(root)
    max_num_input.place(relx=0.1, rely=0.35, relwidth=0.3, relheight=0.1)
    answer_path_input = Entry(root)
    answer_path_input.place(relx=0.1, rely=0.5, relwidth=0.3, relheight=0.1)
    test_path_input = Entry(root)
    test_path_input.place(relx=0.1, rely=0.65, relwidth=0.3, relheight=0.1)

    commit_1 = Button(root, text='开始生成', command=bitter_gen_work)
    commit_1.place(relx=0.6, rely=0.275, relwidth=0.3, relheight=0.1)
    commit_2 = Button(root, text='开始检查', command=bitter_check_work)
    commit_2.place(relx=0.6, rely=0.575, relwidth=0.3, relheight=0.1)

    message = Text(root)
    message.place(rely=0.8, relheight=0.2)

    root.mainloop()
