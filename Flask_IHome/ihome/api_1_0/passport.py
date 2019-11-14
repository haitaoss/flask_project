# coding:utf-8
# passport就是认证的意思，可以放用户注册登录这些接口
from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db
from ihome.models import User
from sqlalchemy.exc import IntegrityError  # 重复键异常
from ihome import constants
import re


@api.route("/users", methods=["POST"])
def register():
    """
    注册
    请求参数：手机号、短信验证码、密码、确认密码
    参数格式：json
    :return:
    """
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()
    if not req_dict:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 检验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        # 表示格式不对
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    # 判断两次密码是否一直
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    # 业务处理
    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile).decode("utf-8")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")

    # 判断短信验证码是否过期
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

    # 删除redis中的短信验证码，防止重复校验
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    print(real_sms_code, sms_code)

    # 判断用户填写的短信验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    """
    盐值 salt(盐值就是小随机数)
    用户1 password="123" + (def)盐值 sha1加密 sjdfkalsjfa
    用户2 password="123" + (asd)盐值 sha1加密 sqwewqrqwrk
    
    sha1加密是不可逆的，所以只能通过原始字符串，进行sha1加密，把加密的结果和数据库查询的结果进行比较
    现在sha1加密也不行了，也能通过暴力破解出来，现在使用sha256
    """
    # 保存用户
    user = User(name=mobile, mobile=mobile)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误，后的回滚
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经被注册过")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id
    # 返回应答
    return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route("/sessions", methods=["POST"])
def login():
    """
    用户登录
    参数：手机号，密码
    :return:
    """

    # 提取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")
    # 校验参数
    # 参数完整性校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验手机号的格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的手机号")

    # 判断错误次数是超过限制，如果超过限制，则返回
    # redis记录："access_nums_请求的ip地址":"次数"
    user_ip = request.remote_addr  # 用户的ip地址
    try:
        access_nums = redis_store.get("access_nums_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后重试")

    # 业务处理
    # 从数据库中，根据手机号查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    # 细节，为了防止，别人暴力破解，不要暴露具体的错误信息。
    # 从数据库的密码与用户填写的密码进行对比校验
    if user is None or not user.check_password(password):
        # 记录错误次数
        try:
            # redis的incr ，加一操作
            redis_store.incr("access_nums_%s" % user_ip)
            # 设置有效期
            redis_store.expire("access_nums_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        #  如果验证失败，记录错误次数，返回信息
        return jsonify(errno=RET.DATAERR, errmsg="用户名或者密码错误")

    # 如果验证相同，保存登录状态，在session中
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id
    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登录状态"""

    # 尝试从session获取用户的名字
    name = session.get("name")
    if name:
        return jsonify(errno=RET.OK, errmsg="True", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="False")


@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""
    # 因为，浏览器访问的时候，会把cookie都传送过来
    # 这个时候，我们就获取了这个浏览器对应的session_id，
    # 所以这里的clear是清除这个sessin_id的信息，不会把别人的清除掉
    csrf_token = session.get("csrf_token")  # 先获取出来
    session.clear()
    session['csrf_token'] = csrf_token  # 在设置回去
    return jsonify(errno=RET.OK, errmsg="OK")
