# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag, put_data
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'glePOQvmsQeNjvVNVIH3FyJClgXSrNRhOVT4DQEI'
secret_key = '64RQeycTsW2wu5Y2FTErut40B5Yw4zFRRXJzT0sb'


def storage(file_data):
    """
    上传文件到七牛
    :param file_data: 要上传文件的二进制数据
    :return:
    """

    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ss-flask-ihome'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)  # 不取名字就设置成None

    ret, info = put_data(token, None, file_data)  # 这是直接给二进制数据

    # print(info)
    # print("*" * 10)
    # print(ret)
    if info.status_code == 200:
        # 表示上传成功,返回文件名
        return ret.get("key")
    # 上传失败
    raise Exception("上传七牛失败")


if __name__ == '__main__':
    with open("./auth.html") as file:
        storage(file.read())
