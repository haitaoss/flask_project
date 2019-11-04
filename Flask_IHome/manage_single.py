from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import redis

app = Flask(__name__)


class Config(object):
    """配置信息"""

    DEBUG = True
    SECRET_KEY = 'SADJF1229*&^*^#SLDFAKDS'

    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/flaks_ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # reids
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 10
    # flask_session
    SESSION_TYPE = 'redis'  # 用作保存session的类型
    SESSION_REDIS = redis.StrictRedis(port='127.0.0.1', host=6379, db=9)  # redis实例
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行加密处理
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # session数据的有效期，单位秒


app.config.from_object(Config)
# 数据库
db = SQLAlchemy(app)

# 创建redis连接对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB)

# 利用flask_session，将session数据保存保存到别的地方,这里选择redis
Session(app)  # 他读取app里面的配置项，最终修改app保存session数据的方式

# 为flask补充csrf防护
CSRFProtect(app)  # 会利用flask里面的钩子，实现添加csrf验证


@app.route('/index')
def index():
    return 'index page'


if __name__ == '__main__':
    app.run()
