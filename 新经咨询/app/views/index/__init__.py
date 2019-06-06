# 导入蓝图
from flask import Blueprint

# 创建蓝图

index_blu = Blueprint("index_blu", __name__)

from . import views