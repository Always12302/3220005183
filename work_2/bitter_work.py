import random
from line_profiler_pycharm import profile


@profile
def gcd(a, b):  # 使用辗转相除法计算两个数的最大公因子

    if a % b == 0:
        return b
    else:
        return gcd(b, a % b)


@profile
def reduce(string):  # 对一个分数进行约分

    a_b = string.split("/")
    a = int(a_b[0])
    b = int(a_b[1])
    max_factor = gcd(a, b)
    after_a = a // max_factor
    after_b = b // max_factor
    after_string = str(after_a) + "/" + str(after_b)
    if after_b == 1:
        after_string = str(after_a)
    return after_string


@profile
def gen_fraction(max_num):  # 生成一个真分数

    mother = random.randint(2, max_num-1)
    son = random.randint(1, mother-1)
    after_string = str(son) + "/" + str(mother)
    fraction = reduce(after_string)
    return fraction


@profile
def gen_number(max_num):  # 生成数字

    if max_num == 1:
        mother = random.randint(2, 100)
        son = random.randint(1, mother - 1)
        after_string = str(son) + "/" + str(mother)
        number = reduce(after_string)
    else:
        flag = random.randint(0, 2)
        if flag == 0:
            number = str(random.randint(1, max_num-1))
        elif flag == 1:
            number = gen_fraction(max_num)
        elif flag == 2:
            number = str(random.randint(1, max_num-1)) + "‘" + gen_fraction(max_num)
    return number


@profile
def gen(max_num):  # 生成表达式

    expression = []
    number = gen_number(max_num)
    expression.append(str(number))
    d = random.randint(1, 3)
    s = d
    while d > 0:
        symbol_flag = random.randint(1, 4)
        if symbol_flag == 1:
            expression.append("+")
        elif symbol_flag == 2:
            expression.append("-")
        elif symbol_flag == 3:
            expression.append("*")
        else:
            expression.append("÷")
        number = gen_number(max_num)
        expression.append(str(number))
        d = d - 1
    if s == 3:
        while True:
            left_flag = random.choice([0, 2, 4])
            right_flag = random.choice([2, 4, 6])
            if left_flag < right_flag and right_flag - left_flag != 6:
                expression.insert(left_flag, "(")
                expression.insert(right_flag+2, ")")
                break
    if s == 2:
        while True:
            left_flag = random.choice([0, 2])
            right_flag = random.choice([2, 4])
            if left_flag < right_flag and right_flag - left_flag != 4:
                expression.insert(left_flag, "(")
                expression.insert(right_flag + 2, ")")
                break
    string = " ".join(expression)
    value = calculate_all(expression)
    return Expression(string, value)


@profile
def calculate_1(num_1, num_2):  # 加法运算

    if num_1.find("False") > -1 or num_2.find("False") > -1:
        return "False"
    if num_1.find("/") > -1:
        son_1 = int(num_1.split("/")[0])
        mother_1 = int(num_1.split("/")[1])
        if num_2.find("/") > -1:
            son_2 = int(num_2.split("/")[0])
            mother_2 = int(num_2.split("/")[1])
            son_3 = son_1 * mother_2 + son_2 * mother_1
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == mother_3:
                number = 1
        else:
            son_2 = int(num_2)
            mother_2 = 1
            son_3 = son_1 * mother_2 + son_2 * mother_1
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == mother_3:
                number = 1
    else:
        son_1 = int(num_1)
        mother_1 = 1
        if num_2.find("/") > -1:
            son_2 = int(num_2.split("/")[0])
            mother_2 = int(num_2.split("/")[1])
            son_3 = son_1 * mother_2 + son_2 * mother_1
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == mother_3:
                number = 1
        else:
            son_2 = int(num_2)
            mother_2 = 1
            son_3 = son_1 * mother_2 + son_2 * mother_1
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if mother_3 == 1:
                number = str(son_3)
            if son_3 == mother_3:
                number = 1
    return str(number)


@profile
def calculate_2(num_1, num_2):  # 减法运算

    if num_1.find("False") > -1 or num_2.find("False") > -1:
        return "False"
    if num_1.find("/") > -1:
        son_1 = int(num_1.split("/")[0])
        mother_1 = int(num_1.split("/")[1])
        if num_2.find("/") > -1:
            son_2 = int(num_2.split("/")[0])
            mother_2 = int(num_2.split("/")[1])
            son_3 = son_1 * mother_2 - son_2 * mother_1
            if son_3 < 0:
                return "False"
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
        else:
            son_2 = int(num_2)
            mother_2 = 1
            son_3 = son_1 * mother_2 - son_2 * mother_1
            if son_3 < 0:
                return "False"
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
    else:
        son_1 = int(num_1)
        mother_1 = 1
        if num_2.find("/") > -1:
            son_2 = int(num_2.split("/")[0])
            mother_2 = int(num_2.split("/")[1])
            son_3 = son_1 * mother_2 - son_2 * mother_1
            if son_3 < 0:
                return "False"
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
        else:
            son_2 = int(num_2)
            mother_2 = 1
            son_3 = son_1 * mother_2 - son_2 * mother_1
            if son_3 < 0:
                return "False"
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
    return str(number)


@profile
def calculate_3(num_1, num_2):  # 乘法运算

    if num_1.find("False") > -1 or num_2.find("False") > -1:
        return "False"
    if num_1.find("/") > -1:
        son_1 = int(num_1.split("/")[0])
        mother_1 = int(num_1.split("/")[1])
        if num_2.find("/") > -1:
            son_2 = int(num_2.split("/")[0])
            mother_2 = int(num_2.split("/")[1])
            son_3 = son_1 * son_2
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
        else:
            son_2 = int(num_2)
            mother_2 = 1
            son_3 = son_1 * son_2
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
    else:
        son_1 = int(num_1)
        mother_1 = 1
        if num_2.find("/") > -1:
            son_2 = int(num_2.split("/")[0])
            mother_2 = int(num_2.split("/")[1])
            son_3 = son_1 * son_2
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
        else:
            son_2 = int(num_2)
            mother_2 = 1
            son_3 = son_1 * son_2
            mother_3 = mother_1 * mother_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
    return str(number)


@profile
def calculate_4(num_1, num_2):  # 除法运算

    if num_1.find("False") > -1 or num_2.find("False") > -1:
        return "False"
    if num_2 == "0":
        return "False"
    if num_1.find("/") > -1:
        son_1 = int(num_1.split("/")[0])
        mother_1 = int(num_1.split("/")[1])
        if num_2.find("/") > -1:
            son_2 = int(num_2.split("/")[0])
            mother_2 = int(num_2.split("/")[1])
            son_3 = son_1 * mother_2
            mother_3 = mother_1 * son_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
        else:
            son_2 = int(num_2)
            mother_2 = 1
            son_3 = son_1 * mother_2
            mother_3 = mother_1 * son_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
    else:
        son_1 = int(num_1)
        mother_1 = 1
        if num_2.find("/") > -1:
            son_2 = int(num_2.split("/")[0])
            mother_2 = int(num_2.split("/")[1])
            son_3 = son_1 * mother_2
            mother_3 = mother_1 * son_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
        else:
            son_2 = int(num_2)
            mother_2 = 1
            son_3 = son_1 * mother_2
            mother_3 = mother_1 * son_2
            number = str(son_3) + "/" + str(mother_3)
            number = reduce(number)
            if son_3 == 0:
                number = 0
            if son_3 == mother_3:
                number = 1
    return str(number)


@profile
def reshape(num_str):  # 从带分数转换成分数

    int_0 = num_str.split("‘")[0]
    son_0 = num_str.split("‘")[1].split("/")[0]
    mother_0 = num_str.split("‘")[1].split("/")[1]
    son_1 = int(int_0) * int(mother_0) + int(son_0)
    number = str(son_1) + "/" + str(mother_0)
    return number


@profile
def calculate(str_list):  # 计算一段表达式的值

    i = 0
    while i < len(str_list):
        if str_list[i].count("‘") > 0:
            str_list[i] = reshape(str_list[i])
        i = i + 1
    if str_list.count("*") == 0 and str_list.count("÷") == 0:
        i = 0
        while i < len(str_list):
            if str_list[i] == "+":
                value = calculate_1(str_list[i - 1], str_list[i + 1])
                str_list[i + 1] = str(value)
            elif str_list[i] == "-":
                value = calculate_2(str_list[i - 1], str_list[i + 1])
                str_list[i + 1] = str(value)
            i = i + 1
    elif str_list.count("+") == 0 and str_list.count("-") == 0:
        i = 0
        while i < len(str_list):
            if str_list[i] == "*":
                value = calculate_3(str_list[i - 1], str_list[i + 1])
                str_list[i + 1] = str(value)
            elif str_list[i] == "÷":
                value = calculate_4(str_list[i - 1], str_list[i + 1])
                str_list[i + 1] = str(value)
            i = i + 1
    else:
        if str_list.count("÷") == 0:
            symbol_3_index = str_list.index("*")
            if str_list.count("-") == 0:
                symbol_1_index = str_list.index("+")
                value = calculate_3(str_list[symbol_3_index-1], str_list[symbol_3_index+1])
                str_list[symbol_3_index - 1] = value
                str_list[symbol_3_index + 1] = value
                value = calculate_1(str_list[symbol_1_index-1], str_list[symbol_1_index+1])
            else:
                symbol_2_index = str_list.index("-")
                value = calculate_3(str_list[symbol_3_index-1], str_list[symbol_3_index+1])
                str_list[symbol_3_index - 1] = value
                str_list[symbol_3_index + 1] = value
                value = calculate_2(str_list[symbol_2_index-1], str_list[symbol_2_index+1])
        else:
            symbol_4_index = str_list.index("÷")
            if str_list.count("-") == 0:
                symbol_1_index = str_list.index("+")
                value = calculate_4(str_list[symbol_4_index-1], str_list[symbol_4_index+1])
                str_list[symbol_4_index - 1] = value
                str_list[symbol_4_index + 1] = value
                value = calculate_1(str_list[symbol_1_index-1], str_list[symbol_1_index+1])
            else:
                symbol_2_index = str_list.index("-")
                value = calculate_4(str_list[symbol_4_index-1], str_list[symbol_4_index+1])
                str_list[symbol_4_index - 1] = value
                str_list[symbol_4_index + 1] = value
                value = calculate_2(str_list[symbol_2_index-1], str_list[symbol_2_index+1])
    return value


@profile
def calculate_all(str_list):  # 计算整个表达式的值

    if str_list.count("(") == 0:
        value = calculate(str_list)
    else:
        left_index = str_list.index("(")
        right_index = str_list.index(")")
        sub_str_list_1 = str_list[left_index + 1:right_index]
        value = calculate(sub_str_list_1)
        if value:
            sub_str_list_2 = str_list[0:left_index] + [value] + str_list[right_index + 1:len(str_list)]
            value = calculate(sub_str_list_2)
    if value:
        if value.count("/") > 0:
            string = str(value)
            son_0 = string.split("/")[0]
            mother_0 = string.split("/")[1]
            int_0 = int(son_0) // int(mother_0)
            son_0 = int(son_0) % int(mother_0)
            fraction = str(son_0) + "/" + str(mother_0)
            fraction = reduce(fraction)
            if int_0 == 0:
                value = fraction
            else:
                value = str(int_0) + "‘" + fraction
    return value


class Expression:  # 定义一个表达式的类 含有表达式和值两个属性

    def __init__(self, string, value):
        self.string = string
        self.value = value


@profile
def gen_work(expression_num, max_num):  # 生成表达式并计算表达式的值 后存放进指定文件

    expression_write = open("Exercises.txt", "w")
    answer_write = open("Answers.txt", "w")
    expression_list = []
    i = 0
    while i < 64:
        expression_list.append([])
        i += 1
    i = 0
    while i < expression_num:
        expression = gen(max_num)
        pass_repeat = len(list(filter(lambda X: X.string == expression.string,
                                      expression_list[len(expression.string)]))) == 0
        if expression.value != "False" and pass_repeat:
            expression_list[len(expression.string)].append(expression)
            i += 1
    expressions = []
    for expression in expression_list:
        expressions.extend(expression)
    random.shuffle(expressions)
    all_expression = ""
    all_answer = ""
    for i in range(len(expressions)):
        all_expression += (str(i+1) + "、\n" + expressions[i].string + " =\n")
        all_answer += (str(i+1) + "、\n" + expressions[i].value + '\n')
    expression_write.write(all_expression)
    answer_write.write(all_answer)
    expression_write.close()
    answer_write.close()

    tip = "已生成 " + str(expression_num) + " 道 " + str(max_num) + " 以内的四则运算题 题目存放于Exercises.txt 答案存放于Answers.txt"
    print(tip)
    return tip


@profile
def check_work(answer_path, test_path):  # 检查答案文件与测试文件的差别 统计正确和错误情况

    answer = open(answer_path, "r")
    test = open(test_path, "r")
    count = len(open(answer_path, "r").readlines())
    true_list = []
    false_list = []
    i = 0
    while i < count/2:
        answer.readline()
        test.readline()
        if answer.readline() == test.readline():
            true_list.append(str(i+1))
        else:
            false_list.append(str(i+1))
        i = i + 1
    tip_1 = "Correct: " + str(len(true_list)) + " (" + ", ".join(true_list) + ")"
    tip_2 = "Wrong: " + str(len(false_list)) + " (" + ", ".join(false_list) + ")"
    print(tip_1)
    print(tip_2)
    tip_3 = tip_1 + "\n" + tip_2 + "\n成绩存放于Grade.txt"
    grade_path = "Grade.txt"
    grade = open(grade_path, "w")
    grade.write(tip_3)
    grade.close()
    return tip_3


if __name__ == '__main__':

    gen_work(100, 10)
