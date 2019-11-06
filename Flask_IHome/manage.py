from ihome import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand  # 迁移的执行者和迁移的命令

# 创建flask的应用对象
app = create_app("develop")

# 创建管理者
manager = Manager(app)
# 把Migrate创建出来的迁移者对象保存到app中
Migrate(app, db)
# 添加命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
