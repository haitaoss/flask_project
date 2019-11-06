import redis


class Config(object):
    """配置信息"""

    SECRET_KEY = 'SADJF1229*&^*^#SLDFAKDS'
    import pymysql
    pymysql.install_as_MySQLdb()
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/flask_ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # reids
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 10
    # flask_session
    SESSION_TYPE = 'redis'  # 用作保存session的类型
    SESSION_REDIS = redis.StrictRedis(host='127.0.0.1', port=6379, db=9)  # redis实例
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行加密处理
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # session数据的有效期，单位秒


class DevelopmentConfig(Config):
    """开发模式"""
    DEBUG = True


class ProductionConfig(Config):
    """生产模式"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
