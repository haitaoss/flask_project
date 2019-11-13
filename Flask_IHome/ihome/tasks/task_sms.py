from celery import Celery
from ihome.libs.yuntongxun.sms import CCP

# 定义Celery对象,参数应用的名字，中间人是谁
# 一般名字是你这个文件的存放路径（在项目里面的存放路径，目的是启动工作者的时候要一样）
app = Celery("ihome.task.task_sms", broker="redis://127.0.0.1:6379/3")


@app.task
def send_sms(mobile, datas, temp_id):
    """发送短信的异步任务"""
    ccp = CCP()
    ccp.send_template_sms(mobile, datas, temp_id)
