# coding:utf-8
from . import api
from flask import request, jsonify, current_app, g,session
from ihome.utils.response_code import RET
from ihome.utils.commons import login_require
from ihome.utils.image_storage import storage
from ihome.utils.image_storage_fdfs import upload_image
from ihome import redis_store, db
from ihome.models import Area, House, Facility, HouseImage, Order,User
from ihome import constants
from datetime import datetime
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
        # file_name = storage(image_data)
        file_name = upload_image(image_data)
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


# /api/v1.0/houses?sd=2017-12-01&ed=2017-12-31&aid=10&sk=new&p=1
# 开始时间，结束换时间，区域id，排序方式，页码数
@api.route('/houses')
def get_house_list():
    """获取房屋的列表信息（搜索页面）"""
    begin_date = request.args.get("sd", "")  # 用户想要的起始时间
    end_date = request.args.get("ed", "")  # 用户想要的结束时间
    area_id = request.args.get("aid", "")  # 区域id
    sort_key = request.args.get("sk", "new")  # 排序关键字
    page = request.args.get("p", "")  # 页数

    # 处理时间
    try:
        if begin_date:
            # 时间字符串变成时间对象 2014-01-01
            begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
        if end_date:
            # 时间字符串变成时间对象 2014-01-01
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if begin_date and end_date:
            assert end_date > begin_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")

    # 判断区域id
    if area_id:
        try:
            Area.query.get(area_id)  # 这里主要是判断数据格式的问题，
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="区域参数有误")
    # 处理页数

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    if page <= 0:
        page = 1

    # 从缓存中获取数据
    redis_key = "house_%s_%s_%s_%s" % (begin_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            current_app.logger.info("从redis中获取到缓存数据 house_%s_%s_%s_%s")
            return resp_json, 200, {"Content-Type": "application/json"}

    # 过滤条件的参数列表容器
    filter_params = []

    # 时间条件
    confict_orders = None
    try:
        # 填充过滤参数,,,查询冲突的订单
        if begin_date and end_date:
            # 查询下过订单的房子，时间和我们冲突。然后把冲突的过滤掉(逆向思维)
            # 查询冲突的房子
            # select * from order where order.begin_date<=end_date
            # and order.end_date>=begin_date;
            # 查询冲突的订单
            confict_orders = Order.query().filter(Order.begin_date <= end_date,
                                                  Order.end_date >= begin_date).all()

        elif begin_date:
            confict_orders = Order.query.filter(Order.end_date >= begin_date).all()

        elif end_date:
            confict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if confict_orders:
        confict_house_ids = [order.id for order in confict_orders]  # 列表推导式

        if confict_house_ids:
            # 这个涉及到等号参数的说明，看看demo
            filter_params.append(House.id.notin_(confict_house_ids))

    # 区域条件
    if area_id:
        filter_params.append(House.area_id == area_id)

    # 查询数据库
    # 补充排序条件，这里并没有查询数据库
    if sort_key == "booking":  # 入住最多
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())  # 拆包，还可以拆列表
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())  # 拆包，还可以拆列表
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:  # 新旧
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())  # 拆包，还可以拆列表

    # House.query.paginate()
    try:
        # 处理分页
        #                               当前页数        每页数据                                        错误输出（默认出错就报错）
        page_obj = house_query.paginate(page=page, per_page=constants.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    # 获取页面数据
    houses_li = page_obj.items
    houses = []
    for house in houses_li:
        houses.append(house.to_basic_dict())

    # 获取总页数
    total_page = page_obj.pages

    # 将数据变成json字符串
    resp_dict = dict(errno=RET.OK,
                     errmsg="OK",
                     data={
                         "total_page": total_page,
                         "houses": houses,
                         "current_page": page
                     })
    resp_json = json.dumps(resp_dict)
    # 将数据存入redis缓存
    if page <= total_page:
        redis_key = "house_%s_%s_%s_%s" % (begin_date, end_date, area_id, sort_key)
        try:
            # redis_store.hset(redis_key, page, resp_json)
            # redis_store.expire(redis_store, constants.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)
            # 创建redis管道对象，可以一次执行多个语句
            pipeline = redis_store.pipeline()

            # 开启多个语句的记录
            pipeline.multi()

            # 向管道添加待执行的语句
            pipeline.hset(redis_key, page, resp_json)
            pipeline.expire(redis_key, constants.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)

            # 执行语句
            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)

    # 响应
    return resp_json, 200, {"Content-Type": "application/json"}


@api.route("/user/houses", methods=["GET"])
@login_require
def get_user_houses():
    """获取房东发布的房源信息条目"""
    user_id = g.user_id

    try:
        # House.query.filter_by(user_id=user_id)
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    # 将查询到的房屋信息转换为字典存放到列表中
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})


@api.route("/houses/index", methods=["GET"])
def get_house_index():
    """获取主页幻灯片展示的房屋基本信息"""
    # 从缓存中尝试获取数据
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        ret = None

    if ret:
        current_app.logger.info("hit house index info redis")
        # 因为redis中保存的是json字符串，所以直接进行字符串拼接返回
        return '{"errno":0, "errmsg":"OK", "data":%s}' % ret, 200, {"Content-Type": "application/json"}
    else:
        try:
            # 查询数据库，返回房屋订单数目最多的5条数据
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="查询无数据")

        houses_list = []
        for house in houses:
            # 如果房屋未设置主图片，则跳过
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())

        # 将数据转换为json，并保存到redis缓存
        json_houses = json.dumps(houses_list)  # "[{},{},{}]"
        try:
            redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
        except Exception as e:
            current_app.logger.error(e)

        return '{"errno":0, "errmsg":"OK", "data":%s}' % json_houses, 200, {"Content-Type": "application/json"}


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """获取房屋详情"""
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则不展示，
    # 所以需要后端返回登录用户的user_id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id，否则返回user_id=-1
    user_id = session.get("user_id", "-1")

    # 校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数确实")

    # 先从redis缓存中获取信息
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info("hit house info redis")
        return '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, ret), \
               200, {"Content-Type": "application/json"}

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 将房屋对象数据转换为字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据出错")

    # 存入到redis中
    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        current_app.logger.error(e)

    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, json_house), \
           200, {"Content-Type": "application/json"}
    return resp
