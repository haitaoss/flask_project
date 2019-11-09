# coding:utf-8
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome.libs.yuntongxun.sms import CCP
from ihome import redis_store, constants
from flask import current_app, jsonify, make_response, request
from ihome.models import User
import random


# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    : params image_code_id: 图片验证码编号
    :return: 正常：验证码图片 异常：返回json数据
    """

    # 提取参数
    # 检验参数 ,不穿根本就进不来，所以不需要判断了
    # 业务逻辑处理
    # 生成验证码图片
    name, text, image_data = captcha.generate_captcha()  # 名字，真实文本，图片数据
    # text, image_data = captcha2.veri_code()
    # 将验证码真实值与编号保存到redis中
    # redis: 字符串 列表 哈希 set sortset
    # "key" :xxx

    # 使用哈希维护有效期的时候，只能整体操作
    # 使用单条维护记录，选用字符串
    # "image_code_编号1":"真实值"
    #                   记录名                             有效期                       值
    try:  # 链接redis数据库，链接超时出现异常
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_EXPIRES, text)  # 有效期
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)  # 不需要记录访问的路径试图，这里的e就是message的值。自己去看看代码理解一下
        # return jsonify(errno=RET.DBERR, errmsg="save image code id failed")
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码信息失败")
    # 返回应答,可以是字符串，或者是图片,但是默认的Content-Type:text/html不是图片的头
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


# GET /api/v1.0/sms_codes/<mobile>?image_code=xx&image_code_id=xx
@api.route('/sms_codes/<re(r"1[345678]\d{9}"):mobile>')
def get_sms_code(mobile):
    """获取短信验证"""
    # 提取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 校验参数
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 业务处理:发送短信
    # 从redis中取出真实的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 判断图片验证码是否过期
    if real_image_code is None:
        # 表示图片验证码没有或者过期
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")
    # 删除图片验证码，防止用户使用同一个验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 与用户填写的值进行对比
    if real_image_code.decode('utf-8').upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码错误")

    # 判断发送短信是否超过60秒
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        # 记录错误日志
        current_app.logger.error(e)
    else:
        if send_flag:
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，60秒后重试")

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        # return jsonify(errno=RET.DATAERR, errmsg="数据库出错")
        # 这里不要return，这是数据库问题，万一手机号真的没有注册过
        # 你在这里抛出已被注册，不就浪费一个客户了码。
        # 我们在最终用户点击，注册按钮的时候，会再次判断手机号是否被注册过
        # 所以这里，当做没被注册过，往下面执行
    else:
        if user is not None:
            # 表示手机号已经存在
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已被注册")
    # 手机号不存在，则生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)  # 最少是6位数，不够补0

    # 保存真实的短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户在60s内再次发送短信的操作
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL_EXPIRES, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")
    # 发送短信验证码
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_EXPIRES / 60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")

    # 返回值
    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg="发送成功")

    return jsonify(errno=RET.THIRDERR, errmsg="发送失败")
