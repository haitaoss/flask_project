# coding:utf-8
# 图片验证码的redis有效期，单位：秒
IMAGE_CODE_EXPIRES = 180

# 短信验证码的redis有效期，单位：秒
SMS_CODE_EXPIRES = 300

# 发送短信验证码的间隔，单位：秒
SEND_SMS_CODE_INTERVAL_EXPIRES = 60

# 登录错误尝试次数
LOGIN_ERROR_MAX_TIMES = 5

# 登录错误限制的时间,单位：秒
LOGIN_ERROR_FORBID_TIME = 600

# 七牛的域名
QINIU_URL_DOMAIN = "http://q0w7mhayl.bkt.clouddn.com/"
# QINIU_URL_DOMAIN = "http://192.168.205.148:8888/"

# 城区信息的缓存时间,单位：秒
AREA_INFO_REDIS_CACHE_EXPIRES = 7200

# fdfs配置文件的路径
FDFS_CLIENT_CONFIG_PATH = "/ihome/utils/client.conf"

# 房屋列表页面，每页数据容量
HOUSE_LIST_PAGE_CAPACITY = 2

# 房屋列表页面页数缓存时间，单位秒
HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200
