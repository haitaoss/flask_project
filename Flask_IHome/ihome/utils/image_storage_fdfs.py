from fdfs_client.client import Fdfs_client
from ihome import constants
import sys


def upload_image(image_data):
    """
    上传图片
    :param image_data: 图片的二进制数据
    :return: 返回图片的访问路径
    """

    # 创建Fdfs_client对象

    client = Fdfs_client(sys.path[0] + constants.FDFS_CLIENT_CONFIG_PATH)
    # 上传文件的流
    res = client.upload_by_buffer(image_data)
    # return dict
    # {
    #     'Group name': group_name,
    #     'Remote file_id': remote_file_id,
    #     'Status': 'Upload successed.',
    #     'Local file name': '',
    #     'Uploaded size': upload_size,
    #     'Storage IP': storage_ip
    # }
    if res.get('Status') != 'Upload successed.':
        # 上传失败
        raise Exception('上传文件到fast dfs失败')
    # 获取返回文件的ID
    filename = res.get("Remote file_id")

    return filename


if __name__ == '__main__':
    upload_image("")
