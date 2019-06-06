# 导入蓝图
from flask import Blueprint

# 创建蓝图
user_blu = Blueprint("user", __name__)

from . import views
