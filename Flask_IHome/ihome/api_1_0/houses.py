# coding:utf-8
from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db
from ihome.models import Area
from sqlalchemy.exc import IntegrityError  # 重复键异常
from ihome import constants
import re
import json


@api.route("/areas")
def get_area_info():
    """获取城区信息"""
    # 尝试从redis中获取数据
    try:
        resp_json_str = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json_str:
            # 有缓存数据
            current_app.logger.info("从redis中获取到缓存数据 area_info")
            return resp_json_str, 200, {"Content-Type": "application/json"}

    # 查询数据库,获取城区信息
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    area_dict_li = []
    # 将对象变成字典
    for area in area_li:
        area_dict_li.append(area.to_dic())

    # 将数据转换为json字符串,把整体转换成json字符串方便
    # resp_json_str = json.dumps({"errno": RET.OK, "errmsg": "ok", "data": area_dict_li})
    resp_json_str = json.dumps(dict(errno=RET.OK, errmsg="ok", data=area_dict_li))

    # 将数据保存到redis中
    try:
        # 必须设置有效期，防止我们忘记修数据库信息的时候删除redis的缓存
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json_str)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json_str, 200, {"Content-Type": "application/json"}
