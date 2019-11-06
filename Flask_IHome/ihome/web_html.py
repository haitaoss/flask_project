# 提供静态页面的蓝图
# 因为http://127.0.0.1:5000/static/html/index.html
# 这种访问方式不友好
from flask import Blueprint
from flask import current_app

# 提供静态文件的蓝图
html = Blueprint('web_html', __name__)


# 127.0.0.1:5000/
# 127.0.0.1:5000/index.html
# 127.0.0.1:5000/register.html
# 127.0.0.1:5000/register.html # 浏览器认为的网站标识，浏览器会自己请求资源
@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    """提供html文件"""
    # 如果html_file_name为“”，标识访问的路径是/ 请求的是主页
    if not html_file_name:
        html_file_name = 'index.html'
    # 如果资源名称不是favicon.ico
    if html_file_name != "favicon.ico":
        html_file_name = 'html/' + html_file_name

    # flask提供的返回静态文件的方法，回去应用的静态资源目录找文件，我们提供/static
    return current_app.send_static_file(html_file_name)
