# coding:utf-8
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome import redis_store, constants
from flask import current_app, jsonify, make_response


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
