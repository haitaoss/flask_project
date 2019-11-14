li1 = [1, 2, 3, 4]
li2 = [2, 3]


def add(num1, num2):
    return num1 + num2


# map函数，参数：函数，调用函数所需的参数
ret = map(add, li1, li2)
print(ret)  # python2 返回的是list，python3返回的是map类型

print(list(ret))

