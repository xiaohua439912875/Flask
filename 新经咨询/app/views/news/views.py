from flask import request, jsonify,g

from app import db
from app.models.models import User,Collection
from app.utils.common.common import login_user_data
from . import news_blu


@news_blu.route("/collect", methods=["POST", "GET"])
@login_user_data
def collect():
    # 1 获取数据
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    print(news_id, action)

    # 判断
    if not all([news_id, action]):
        ret = {
            "errno": 6001,
            "errmsg": "缺少参数"
        }

        return jsonify(ret)

    if not g.user:
        ret = {
            "errno": 4101,
            "errmsg": "未登录"
        }
        return jsonify(ret)

    if action == "do":
        # do 表示添加收藏
        # 插入数据库,此时数据库有lnews模型，news.id,user.id
        collection = Collection()
        collection.user_id = g.user.id  # 对应的用户的id
        collection.news_id = news_id   # 新闻id
        # 提交到数据库
        db.session.add(collection)
        db.session.commit()

        ret = {
            "errno": 0,
            "ermsg": "添加收藏成功"
        }

        return jsonify(ret)

    elif action == "undo":
        # undo 表示取消收藏
        # 思路： 取消收藏表示添加的数据中清空news_id 和 user 对应的id

        # 1 数据查询出来
        collects = db.session.query(Collection).filter(Collection.user_id == g.user.id, Collection.news_id == news_id).first()

        if collects:
            # 清除数据
            db.session.delete(collects)
            db.session.commit()
            ret = {
                "errno": 0,
                "errmsg":"取消收藏成功"
            }

        else:
            ret = {
                "errno": 6002,
                "errmsg": "取消收藏失败"
            }

        return jsonify(ret)

