from flask import session, g
import functools


def login_user_data(view_func):

    from app.models.models import User
    from app import db

    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 尝试从session中获取user_id
        # user_id = session.get('user_id')  # 获取不到，返回None
        user_id = session.get("user_id")

        user = None
        if user_id:
            # 用户已登录
            try:
                user = db.session.query(User).filter(User.id == user_id).first()
            except Exception as e:
                print("提取从User模型类查询，产生异常...")

        # 使用g变量临时保存user信息
        # g变量中保存的数据可以在请求开始到请求结束过程中的使用
        g.user = user
        print(g.user)

        return view_func(*args, **kwargs)
    return wrapper


def show_index_colorful(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""



