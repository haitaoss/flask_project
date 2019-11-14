from . import api
from flask import request, jsonify, current_app
from project_name.utils.response_code import RET


@api.route("/pay", methods=["POST"])
def pay():
    """
    给用户返回支付宝的链接地址
    参数
    {
        "price":""
    }
    :return:
    """
    req_dict = request.get_json()
    price = req_dict.get("price")

    try:
        price = int(price)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式不正确")
    print(price)
    # 调用支付宝SDK
    return jsonify(errno=RET.OK, errmsg="OK")


@api.route("/")
def index():
    return "ok"
