class Config(object):
    SECRET_KEY = "1"
    # 关闭追踪数据库的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:python@localhost:3306/new_flask2?charset=utf8'


class ProductionConfig(Config):
    DEBUG = False


CONFIG = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
