def login_require(func):
    def wrapper(*args, **kwargs):
        print(wrapper.__doc__)
        print(wrapper.__name__)
        pass

    return wrapper


@login_require
def itcast():
    """itcast python"""
    pass


# itcast -> wrapper
print(itcast.__name__)  # wrapper.__name__
print(itcast.__doc__)  # wrapper.__doc__

# 解决办法，
import functools


def login_require2(func):
    # 就是说，把func对象的文档信息，设置到wrapper这个函数中
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(wrapper.__doc__)
        print(wrapper.__name__)
        pass

    return wrapper


@login_require2
def itcast2():
    """itcast python"""
    pass


# itcast -> wrapper
itcast2()
# print(itcast2.__name__)  # wrapper.__name__
# print(itcast2.__doc__)  # wrapper.__doc__
