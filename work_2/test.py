import sys
sys.path.append("./")
from bitter_work import *


if __name__ == '__main__':

    expression_list = ["1", "+", "2/3", "-", "1‘1/3"]
    print("1、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["1", "x", "2/3", "÷", "1‘1/3"]
    print("2、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["1", "+", "2/3", "*", "1‘1/3"]
    print("3、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["(", "1", "+", "2/3", ")", "*", "1‘1/3"]
    print("4、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["1", "÷", "2/3", "+", "1‘1/3"]
    print("5、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["1", "÷", "(", "2/3", "+", "1‘1/3", ")"]
    print("6、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["(", "1", "÷", "2/3", "+", "1‘1/3", ")", "*", "3"]
    print("7、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["1", "÷", "(", "2/3", "+", "1‘1/3", "*", "3", ")"]
    print("8、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["1", "-", "2/3", "-", "1‘1/3"]  # False样本
    print("9、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)

    expression_list = ["1", "÷", "(", "2/3", "-", "2/3", ")"]  # False样本
    print("10、" + " ".join(expression_list) + "=")
    value = calculate_all(expression_list)
    print(value)
