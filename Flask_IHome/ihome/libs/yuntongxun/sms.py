# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from .CCPRestSDK import REST
# from .CCPRestSDK import REST
import random

# 随机六位数的验证码
six_code = "%06d" % random.randint(0, 999999)

# 主帐号
accountSid = '8a216da86e011fa3016e4fe587fe2be9'

# 主帐号Token
accountToken = '7ad3f01719c445a0a32184a6afb4b47a'

# 应用Id
appId = '8a216da86e011fa3016e4fe5885f2bf0'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

class CCP(object):
    """发送短信验证码，单例模式"""

    def __new__(cls):
        # 判断有没有类属性instance
        if not hasattr(cls, "instance"):
            # 如果没有，则创建这个类的对象，并保存到类属性instance中
            obj = super(CCP, cls).__new__(cls)

            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            # 添加类属性
            cls.instance = obj

        # 如果有，则直接返回对象
        return cls.instance

    # sendTemplateSMS(手机号码,内容数据,模板Id)
    def send_template_sms(self, to, datas, temp_id=1):

        # 调用云通讯的工具rest发送短信
        result = self.rest.sendTemplateSMS(to, datas, temp_id)  # 手机号码,内容数据[验证码,时间],模板Id

        status_code = result.get("statusCode")
        if status_code == "000000":
            # 表示发送成功
            return 0
        else:
            # 发送失败
            return -1


if __name__ == '__main__':
    pass
    # ccp = CCP()
    # ret = ytx.send_template_sms('18389356431', ['1234', "5"], 1)
    # ret = ccp.send_template_sms('18389356431', ['1234', "5"], 1)
    # print(ret)
