from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db


if __name__ == '__main__':
    # 1. 创建flask对象
    app = create_app("development")
    # app.run()
    # 2. 创建Manger对象
    manager = Manager(app)
    # 3. 创建数据库迁移对象
    migrate = Migrate(app, db)
    # 4. 将数据库迁移时的命令添加到manager上
    manager.add_command('db', MigrateCommand)
    # app.run()
    manager.run()
