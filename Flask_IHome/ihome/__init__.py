from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect

import redis
import logging
from logging.handlers import RotatingFileHandler

# 这里不在创建app的时候在创建，是因为，views.py还有models.py在导入的时候就需要，防止找不到

# 数据库
# 这里因为app是在create_app被调用的时候才创建出来，所以推迟初始化
db = SQLAlchemy()

# 创建redis连接对象
redis_store = None

# logging.error("")  # 错误级别
# logging.warn("")  # 警告级别
# logging.info("")  # 消息提示级别
# logging.debug("")  # 调试级别
# debug>info>warn>error

# 配置日志信息
# 设置日志的记录等级
# 如果flask项目的运行模式是DEBUG=True那么这里的配置是无效的。flask会把它设置成debug模型
logging.basicConfig(level=logging.ERROR)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)


# 工厂模式
def create_app(config_name):
    """
    创建flask的应用对象
    :param config_name: str 配置模式的名字 ("develop","product")
    :return:
    """
    app = Flask(__name__)
    # 根据配置文件的名字获取配置参数的类
    app.config.from_object(config_map.get(config_name))

    # 使用app初始化db，这种推迟方法每个flask的扩展都有
    db.init_app(app)

    # 初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=app.config.get('REDIS_HOST'), port=app.config.get('REDIS_PORT'),
                                    db=app.config.get('REDIS_DB'))

    # 利用flask_session，修改flask保存session信息的机制
    Session(app)

    # 为flask补充csrf防护
    CSRFProtect(app)

    # 注册蓝图
    from ihome import api_1_0  # 放在这里是为了解决循环导入的问题
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')
    return app
