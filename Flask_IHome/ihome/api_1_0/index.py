from . import api
from flask import current_app, session, request


@api.route('/index')
def index():
    # logging.error("")  # 错误级别
    # logging.warn("")  # 警告级别
    # logging.info("")  # 消息提示级别
    # logging.debug("")  # 调试级别
    current_app.logger.error("error msg")
    current_app.logger.warn("warn msg")
    current_app.logger.info("info msg")
    current_app.logger.debug("debug msg")

    # request.cookies.get("csrf_token") 正常的csrf校验都是从cookie中获取token
    # session.get("csrf_token")

    # 但是wtf扩展的csrf防护偷了个懒，直接从session中获取(他帮我们生成csrf_token的时候，会自己往session中存一份)

    # 原先的session是保存在cookie中的，我们引入flask_session之后将session信息保存到redis中
    # 客户端浏览器里面的cookie只保存的sessionid
    # 当我们执行退出操作的时候，清除了session，这里只是删掉了redis里面的session数据。浏览器是有缓存策略的，他会在cookie中留着sessionid
    # 当用户再次登录的时候
    # 浏览器里存放的cookie有csrf_token和sessionid。访问的请求头或者表单数据里面确实有csrf_token的值
    # 但是wtf扩展的csrf校验，他没有从cookie中获取csrf_token而是从session中获取csrf_token，但是拿着sessionId是找不到redis里面的session数据的。
    # 也就不会有个 session.get("csrf_token") 
    # 这就出现了  The CSRF tokens do not match.

    return 'index page'
