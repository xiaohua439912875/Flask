from app import db
from app.models.models import News
from app.utils.common.common import login_user_data
from . import admin_blu
from flask import Flask, render_template, g, request, jsonify


@admin_blu.route("/index")
@login_user_data
def index():

    # 后台主页
    return render_template("admin/index.html", user=g.user)


@admin_blu.route("/user_count")
def user_count():
    # 用户统计
    return render_template("admin/user_count.html")


@admin_blu.route("/user_list")
def user_list():
    # 用户列表
    return render_template("admin/user_list.html")


@admin_blu.route("/news_review")
def news_review():
    # 新闻审核
    page = request.args.get("page", 1)

    # 数据库查询
    paginate = db.session.query(News).order_by(News.create_time.desc()).paginate(int(page), 5, False)
    print(paginate)
    news = [x.to_news_list_dict() for x in paginate.items]
    print("----------------2------------")
    print(news)
    return render_template("admin/news_review.html", news=news, paginate=paginate)


@admin_blu.route("/news_review_detail/<news_id>", methods=["POST", "GET"])
def news_review_detail(news_id):
    # print(news_id)
    # 新闻审核是否通过..
    news = db.session.query(News).filter(News.id == news_id).first()

    if request.method == "GET":
        return render_template("admin/news_review_detail.html", news=news)

    elif request.method == "POST":
        # 获取数据
        action = request.json.get("action")
        reason = request.json.get("reason")

        if action == "accept":
            # 通过审核
            news.status = 0
            news.reason = ""

        else:
            # 未审核
            news.status = -1
            news.reason = reason
        try:
            db.session.commit()
            # 操作
            ret = {
                "errno": 0,
                "errmsg": "审核成功"
            }

            return jsonify(ret)

        except Exception as ret:
            ret = {
                "errno":7001,
                "errmsg":"审核失败"
            }

            return jsonify(ret)


@admin_blu.route("/news_edit")
def news_edit():
    # 新闻版式编辑
    # 数据库查询

    return render_template("admin/news_edit.html")


@admin_blu.route("/news_type")
def news_type():
    # 新闻分类管理
    return render_template("admin/news_type.html")

