# coding:utf-8
from . import api
from flask import request, jsonify, current_app, g
from ihome.utils.response_code import RET
from ihome.utils.commons import login_require
from ihome.utils.image_storage import storage
from ihome import redis_store, db
from ihome.models import Area, House, Facility, HouseImage
from ihome import constants
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


@api.route("/houses/info", methods=["POST"])
@login_require
def save_house_info():
    """保存房屋的基本信息
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    """
    # 获取数据

    house_data = request.get_json()

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    # 校验参数
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 判断金额是否正确
    try:
        price = int(float(price) * 100)  # 数据库的单位是以分
        deposit = int(float(deposit) * 100)  # 数据库的单位是以分
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 城区id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    else:
        if not area:
            return jsonify(errno=RET.NODATA, errmsg="城区信息有误")

    # 获取用户id
    user_id = g.user_id

    # 保存房屋信息
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days)
    # 不要再这里，添加，提交，因为房子表的插入和中间表的插入是同一个流程
    # 属于同一个数据，所以在下面统一添加到数据库中
    # try:
    #     db.session.add(house)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="保存数据异常")

    # 处理房屋的设施信息
    facility_li = house_data.get("facility")

    # 如果用户勾选了设施信息，在保存数据库
    if facility_li:
        # ["1","2"]
        # select count(*) from ih_facility_info where id in (1,2)
        try:
            # 这是sqlalcemy的进阶操作
            facilities = Facility.query.filter(Facility.id.in_(facility_li)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")

        if facilities:
            # 有合法的设施数据
            # 保存设置数据
            # 关联字段的进阶使用,他会在保存的时候，会自己在第三张表中插入数据
            house.facilities = facilities
        try:
            db.session.add(house)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")

        # 保存数据成功
        return jsonify(errno=RET.OK, errmsg="ok", data={"house_id": house.id})

@api.route("/houses/image", methods=["POST"])
def save_house_image():
    """保存房屋的图片
    前段发送的数据(多媒体表单数据)
        house_image , house_id
    """
    # 提取参数
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")
    # 校验参数
    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    else:
        if not house:
            return jsonify(errno=RET.NODATA, errmsg="没有房屋信息")

    # 上传图片到七牛
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="保存图片异常")

    # 保存图片到数据库
    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)
    # 保存信息到数据库中
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片数据异常")

    image_url = constants.QINIU_URL_DOMAIN + file_name
    # 保存图片成功
    return jsonify(errno=RET.OK, errmsg="ok", data={"image_url": image_url})
