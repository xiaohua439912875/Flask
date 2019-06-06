# 导入蓝图
from flask import Blueprint

# 创建一个蓝图

admin_blu = Blueprint("admin", __name__)

from . import views