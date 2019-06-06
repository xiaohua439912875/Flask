from flask import Flask

from config import CONFIG

from flask_sqlalchemy import SQLAlchemy

from app.utils.common.common import show_index_colorful  # 导入
# 创建数据库对象
db = SQLAlchemy()


def create_app(config_name):  # config_name=development  main.py中的参数
    from app.views.index import index_blu
    from app.views.admin import admin_blu
    from app.views.passport import passport_blu
    from app.views.user import user_blu
    from app.views.news import news_blu

    # 创建flask应用程序
    app = Flask(__name__)

    # 对flask对象进行配置
    app.config.from_object(CONFIG.get(config_name))

    # 注册蓝图
    app.register_blueprint(index_blu)
    app.register_blueprint(admin_blu, url_prefix="/admin")
    app.register_blueprint(passport_blu, url_prefix="/passport")
    app.register_blueprint(user_blu, url_prefix="/user")
    app.register_blueprint(news_blu, url_prefix="/news")
    # 创建SQLAlchemy对象
    # db = SQLAlchemy(app)  # 需要将创建的flask对象当做参数进行传递，它会自动与flask对象进行关联
    # 应用程序初始化
    # 与此数据库设置一起使用
    # 对db进行配置
    db.init_app(app)

    # 注册过滤器
    app.add_template_filter(show_index_colorful, "show_index_colorful")  # 后面的名字代表了使用过滤器的名字

    return app


