from app import db
from app.utils.common.common import login_user_data
from . import index_blu

from flask import render_template, request, jsonify, session, g

from app.models.models import News


@index_blu.route("/")
@login_user_data
def index():
    # 1. 查询点击排行的前6个数据
    rank_news = db.session.query(News).order_by(News.clicks.desc()).limit(6)  # 从news数据表中查询点击最高的6个数据
    # 获取session数据
    # 如果用户登录成功，那么它就有session值，取出这些值来
    user_id = session.get("user_id")
    nick_name = session.get("nick_name")

    return render_template("index/index.html", rank_news=rank_news, user_id=user_id, nick_name=nick_name, user=g.user)


# 这个试图函数是切换分类要定义的路劲 "GET /newslist?page=1&cid=4&per_page=10 HTTP/1.1" 200 -
@index_blu.route("/newslist")
def newslist():
    # 0. 提取数据
    page = request.args.get("page", 1)
    cid = request.args.get("cid", 0)
    per_page = request.args.get("per_page", 10)

    page = int(page) if page.isalnum() else 1
    cid = int(cid) if cid.isalnum() else 0
    per_page = int(per_page) if per_page.isalnum() else 10

    # 1. 先从数据库中查询
    if cid == 0:
        paginate = db.session.query(News).order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        paginate = db.session.query(News).filter(News.category_id == cid).paginate(page, per_page, False)
    news_list = paginate.items  # 查询出来的对象组成的列表

    # 2. 将查询出来的数据模型对象转化为需要的字典格式
    ret = {
        "totalPage": paginate.pages,
        "newsList": [news.to_dict() for news in news_list]
    }

    # 3. 将字典格式的数据转换为json格式，返回给前端
    # return jsonify(news_list)  # 这种方式不能使用，因为news中是News类的实例对象，使用jsonify不能将其转换为json格式，
    # 所以我们需要，先将news对象转化为普通的字典类型，然后再转化为json
    return jsonify(ret)


@index_blu.route("/detail/<int:news_id>")
@login_user_data
def detail(news_id):
    # 如果用户登录成功，那么它就有session值，取出这些值来
    user_id = session.get("user_id")
    nick_name = session.get("nick_name")
    # 如果这样传递模板变量，能行，但是较为麻烦
    # return render_template("index/detail.html", title="xxxx", create_time="sdfsdf", source="sdf")
    # 合理的做法，是传递一个变量，只要这个变量是一个对象，那么就可以在模板引擎 中使用.属性名来获取数据，更方便
    news = db.session.query(News).filter(News.id == news_id).first()
    rank_news = db.session.query(News).order_by(News.clicks.desc()).limit(6)  # 从news数据表中查询点击最高的6个数据
    author_news = news.user  # 自关联

    author_news.news_num = author_news.news.count()  # 这个是user对象表  # 在user表中新添字段，然后关联news表关联
    author_news.followers_num = author_news.followers.count()
    # print(author_news.followers)

    # 如果用户id在用户粉丝的id的话表示成立
    if user_id in [x.id for x in author_news.followers]:
        author_news.can_follow = False

    else:
        author_news.can_follow = True

    # print(author_news.followers_num) # 粉丝数

    # 收藏判断用户是否关注过
    # g.user and 。。。。 是判断如果第一个g.user是否成立则继续判断下一个
        # 判断当前用户是否已经收藏过此新闻
    try:
        if g.user and (g.user.id in [x.id for x in news.collection_user]):
            # print("收藏过.....")
            g.user.can_collect = False

        else:
            g.user.can_collect = True
    except Exception as ret:
        print(ret)

    return render_template("index/detail.html", news=news,
                           rank_news=rank_news,
                           user_id=user_id,
                           nick_name=nick_name,
                           author_news=author_news,
                           user=g.user)


