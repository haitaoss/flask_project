from . import api
from ihome.utils.commons import login_require
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.utils.image_storage_fdfs import upload_image
from ihome.models import User
from ihome import db, constants

from flask import g, request, current_app, jsonify, session
import re


@api.route("/users/avatar", methods=["POST"])
@login_require  # 得放在下面，自己了解下
def set_user_avatar():
    """设置用户的头像
    参数 图片（以多媒体表单格式），用户id（g.user_id）
    """

    # 装饰器的代码中已经将user_id保存到g对象中，所以视图中可以直接读取
    user_id = g.user_id

    # 获取图片
    image_file = request.files.get("avatar")

    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg="未上传图片")

    # 读取文件数据
    image_data = image_file.read()

    # 调用七牛上传图片，返回文件名
    try:
        # file_name = storage(image_data)
        file_name = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传失败")

    # 保存文件名到数据库中，只保存文件名，不需要保存域名，因为域名都一样，节省数据库的空间
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="保存图片信息失败")

    avatar_url = constants.QINIU_URL_DOMAIN + file_name
    # 保存成功
    return jsonify(errno=RET.OK, errmsg="保存成功", data={"avatar_url": avatar_url})


# @api.route("/users", methods=["GET"])
# @login_require
# def user_profile():
#     """获取用户的信息"""
#     # 获取用户的id
#     user_id = g.user_id
#     # 通过id获取用户的信息,这里肯定不会出现找不到的情况
#     try:
#         user = User.query.filter_by(id=user_id).first()
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(RET.DATAERR, errmsg="数据库异常")
#     # 用户没有图片的情况
#     if not user.avatar_url:
#         user.avatar_url = ""
#     user_info = {
#         "avatar_url": constants.QINIU_URL_DOMAIN + user.avatar_url,
#         "mobile": user.mobile,
#         "name": user.name,
#         "real_name": user.real_name,
#         "id_card": user.id_card
#     }
#
#     # 响应到客户端
#     return jsonify(errno=RET.OK, errmsg="获取成功", data={"user": user_info})


# @api.route("/users", methods=["PUT"])
# # 老师的写法 @api.route("/users/name", methods=["PUT"])
# @login_require
# def update_user():
#     """保存用户信息
#     参数 name
#     """
#     # 提出参数
#     req_dict = request.get_json()
#     if not req_dict:
#         return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
#     name = req_dict.get("name")
#     # 校验参数
#     if not name:
#         return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
#     # 需要更新的数据
#     update_data = {
#         "name": name
#     }
#     # 返回的数据
#     resp_data = {
#         "name": name
#     }
#     if request.args.get("auth"):
#         # 说明是修改认证信息,提取参数
#         real_name = req_dict.get("real_name")
#         id_card = req_dict.get("id_card")
#
#         # 校验参数
#         if not all([real_name, id_card]):
#             return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
#
#         if not re.match(
#                 r"(^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$)|(^[1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{2}[0-9Xx]$)",
#                 id_card):
#             return jsonify(errno=RET.PARAMERR, errmsg="身份证格式不对")
#         # 需要修改的字典
#         update_data = {
#             "real_name": real_name,
#             "id_card": id_card
#         }
#         # 返回的数据
#         resp_data = {
#             "real_name": real_name,
#             "id_card": id_card
#         }
#     # 获取用户的id
#     user_id = g.user_id
#     # 保存用户数据
#     try:
#         User.query.filter_by(id=user_id).update(update_data)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR, errmsg="数据库异常")
#     return jsonify(errno=RET.OK, errmsg="保存成功", data=resp_data)


@api.route("/users/name", methods=["PUT"])
@login_require
def change_user_name():
    """修改用户名"""
    # 使用了login_required装饰器后，可以从g对象中获取用户user_id
    user_id = g.user_id

    # 获取用户想要设置的用户名
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    name = req_data.get("name")  # 用户想要设置的名字
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="名字不能为空")

    # 保存用户昵称name，并同时判断name是否重复（利用数据库的唯一索引)
    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="设置用户错误")

    # 修改session数据中的name字段
    session["name"] = name
    return jsonify(errno=RET.OK, errmsg="OK", data={"name": name})


@api.route("/user", methods=["GET"])
@login_require
def get_user_profile():
    """获取个人信息"""
    user_id = g.user_id
    # 查询数据库获取个人信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@api.route("/users/auth", methods=["GET"])
@login_require
def get_user_auth():
    """获取用户的实名认证信息"""
    user_id = g.user_id

    # 在数据库中查询信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户实名信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())


@api.route("/users/auth", methods=["POST"])
@login_require
def set_user_auth():
    """保存实名认证信息"""
    user_id = g.user_id

    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    real_name = req_data.get("real_name")  # 真实姓名
    id_card = req_data.get("id_card")  # 身份证号

    # 参数校验
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 保存用户的姓名与身份证号
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None) \
            .update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")

    return jsonify(errno=RET.OK, errmsg="OK")
