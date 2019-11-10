from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihome.utils.response_code import RET
import functools


# 定义正则转换器
class ReConverter(BaseConverter):
    """"""

    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # super.__init__(url_map)
        # 保存正则表达式
        self.regex = regex


# 定义的验证登录状态的装饰器
def login_require(view_func):
    # 使用标准库的这个函数装饰器，装饰内层函数。
    # 因为，装饰之后，就不能获取装饰函数的文档信息
    # 加了这个就能就解决这个问题
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get('user_id')
        # 如果用户是登陆的，执行视图函数\
        if user_id:
            # 使用请求上下文g对象，保存数据。
            # 这样子被装饰的函数就能通过g取出保存的值，避免再次从session中获取数据。g.user_id
            g.user_id = user_id
            return view_func(*args, **kwargs)
        # 如果未登录，返回未登录的信息
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    return wrapper

# @login_require
# def set_user_avatar():
#     # user_id = session.get("user_id")
#     user_id = g.user_id
#     pass

# set_user_avatar() -> wrapper()
