import hashlib
import os

from flask import request, session, jsonify, render_template, g, current_app

from app import db
from app.models.models import User, Follow, News, Category
from app.utils.common.common import login_user_data
from . import user_blu


@user_blu.route("/follow", methods=["POST"])
def follow():
    # 提取用户信息
    user_id = session.get("user_id")
    print(user_id)

    # 获取前端数据
    author_id = request.json.get("user_id")  # New 中的user_id
    action = request.json.get("action")
    print("---")
    print(author_id, action)

    # # 逻辑判断
    # if not all([author_id, action]):
    #     ret = {
    #         "errno": 3001,
    #         "errmsg": "缺少参数"
    #     }
    #     return jsonify(ret)

    if not user_id:
        ret = {
            "errno": 3002,
            "errmsg": "未登录"
        }
        return jsonify(ret)

    if action == "do":
        # 关注
        author = db.session.query(User).filter(User.id == user_id).first()
        # print(author)
        # print("=============", author.followers)
        if user_id in [x.id for x in author.followers]:
            ret = {
                "errno": 3003,
                "errmsg": "已经关注成功，请勿重复关注"
            }

            return jsonify(ret)
        try:
            follow = Follow()
            # print(follow)
            follow.followed_id = author_id  # new中的user_id
            follow.follower_id = user_id

            db.session.add(follow)
            db.session.commit()

            ret = {
                "errno": 0,
                "errmsg": "关注成功"

            }
            return jsonify(ret)
        except Exception as ret:
            db.session.rollback()
            ret = {
                "errno":3004,
                "errmsg":"关注失败"
            }
            return jsonify(ret)

    elif action == "undo":
        try:

            follow = db.session.query(Follow).filter(Follow.followed_id== author_id, Follow.follower_id== user_id).first()
            # print(follow)
            # 删除表
            db.session.delete(follow)
            # 增删改要commit
            db.session.commit()
            ret = {
                "errno": 0,
                "errmsg": "取消关注成功"

            }
            return jsonify(ret)

        except Exception as ret:
            db.session.rollback()
            ret = {
                "errno": 3005,
                "errmsg": "取消关注失败"
            }
            return jsonify(ret)


@user_blu.route("/")
@login_user_data
def user():
    user_id = session.get("user_id")
    nick_name = session.get("nick_name")
    return render_template("index/user.html", user_id=user_id, nick_name=nick_name, user=g.user)


@user_blu.route("/user_base_info", methods=["GET", "POST"])
def user_base_info():
    # 获取当前用户的信息
    user_id = session.get("user_id")


    # 存储到数据库
    user = db.session.query(User).filter(User.id == user_id).first()

    if request.method == "GET":
        return render_template("index/user_base_info.html", user=user)
    elif request.method == "POST":
        # 获取用户的新的信息
        nick_name = request.json.get("nick_name")
        signature = request.json.get("signature")
        gender = request.json.get("gender")
        session["nick_names"] = nick_name
        # 判断用户输入的数据是否完整
        if not all([nick_name, gender]):
            ret = {
                "errno": 4001,
                "errmsg": "缺少参数"
            }

            return jsonify(ret)

        if not user:
            ret = {
                "errno": 4002,
                "errmsg": "没有此用户"
            }

            return jsonify(ret)

        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender

        db.session.commit()

        ret = {
            "errno": 0,
            "errmsg": "修改成功"
        }
        return jsonify(ret)


@user_blu.route("/user_pic_info", methods=["POST", "GET"])
@login_user_data
def user_pic_info():
    if request.method == "GET":
        return render_template("index/user_pic_info.html", user=g.user)
    elif request.method == "POST":
        # print(request.files)  # 打印的是图片路径
        f = request.files.get("avatar")
        # print(f)

        if f:
            # 存储到哪个路径呢？文件名叫什么呢？
            file_hash = hashlib.md5()
            file_hash.update(f.filename.encode("utf-8"))
            file_name = file_hash.hexdigest() + f.filename[f.filename.rfind("."):]
            local_file_path = os.path.join("/static/upload/images", file_name)
            file_path = os.path.join(current_app.root_path, "static/upload/images",
                                     file_name)  # f.filename是你刚刚在浏览器选择的那个上传的图片的名字
            # print(file_path)
            # 保存图片的路径
            f.save(file_path)  # a/b/c/123.png

            # 3. 将数据库中对应head_image字段值改为 刚刚保存的图片的路径
            g.user.avatar_url = local_file_path
            print(g.user)
            db.session.commit()

            ret = {
                "errno": 0,
                "errmsg": "上传头像成功",
                "avatar_url":local_file_path
            }
            return jsonify(ret)
        else:
            ret = {
                "errno": 6005,
                "errmsg": "上传头像失败"
            }

            return jsonify(ret)


@user_blu.route("/user_pass_info", methods=["POST", "GET"])
def user_pass_info():
    if request.method == "GET":
        return render_template("index/user_pass_info.html")

    elif request.method == "POST":
        # 查询数据
        # 获取当前用户的信息
        user_id = session.get("user_id")

        # 存储到数据库
        # 判断登入id与查询要修改的id密码是否成立相同
        user = db.session.query(User).filter(User.id == user_id).first()
        # print(user.password_hash)  # 用户当前的密码

        # 获取数据
        # print(request.json)  {'old_password': '123456', 'new_password': '123456', 'new_password2': '123456'}
        old_password = request.json.get("old_password")
        new_password = request.json.get("new_password")
        new_password2 = request.json.get("new_password2")

        # 判断
        if not all([old_password, new_password, new_password2]):
            ret = {
                "errno": 5001,
                "errmsg": "缺少参数"
            }
            return jsonify(ret)

        if old_password != user.password_hash:
            ret = {
                "errno": 5002,
                "errmsg": "当前密码输入错误"
            }
            return jsonify(ret)

        if len(new_password) and len(new_password2) < 6:
            ret = {
                "errno": 5003,
                "errmsg": "密码长度必须6位数"
            }
            return jsonify(ret)

        if new_password != new_password2:
            ret = {
                "errno": 5004,
                "errmsg": "两次密码不一致"
            }
            return jsonify(ret)

        # 都成立的话添加到数据库
        user.password_hash = new_password
        db.session.commit()
        ret = {
            "errno": 0,
            "errmsg": "修改密码成功"
        }
        return jsonify(ret)


@user_blu.route("/user_follow")
@login_user_data
def user_follow():
    """实现我的关注"""
    page = request.args.get("page", 1)

    paginate = g.user.followed.paginate(int(page), 2, False)
    followed_users = [x.to_basic_info() for x in paginate.items]

    # print(len(object_list))

    return render_template("index/user_follow.html", followed_users=followed_users, paginate=paginate)


@user_blu.route("/user_collection")
@login_user_data
def user_collection():
    """我的收藏"""
    page = request.args.get("page", 1)

    paginate = g.user.collection_news.paginate(int(page), 4, False)

    collect = [x.to_collect_dict() for x in paginate.items]
    # print(collect)
    return render_template("index/user_collection.html", collect=collect, paginate=paginate)


@user_blu.route("/user_news_release", methods=["POST", "GET"])
@login_user_data
def user_news_release():
    # 新闻发布
    if request.method == "GET":
        category = db.session.query(Category).filter(Category.id != 1).all()
        return render_template("index/user_news_release.html", category=category)
    elif request.method == "POST":

        title = request.form.get("title")
        category = request.form.get("category")
        digest = request.form.get("digest")
        content = request.form.get("content")
        f = request.files.get("index_images")

        print(f,"--------------------------")
        if not all([title, category, digest, content]):
            ret = {
                "errno": 4006,
                "errmsg": "缺少参数"
            }

            return jsonify(ret)

        if not g.user:
            ret = {
                "errno": 4007,
                "errmsg": "用户未登录"
            }

            return jsonify(ret)
        if f:
            # 保存文件且文件名字是哈希值
            file_hash = hashlib.md5()
            file_hash.update(f.filename.encode("utf-8"))
            file_name = file_hash.hexdigest() + f.filename[f.filename.rfind("."):]
            local_file_path = os.path.join("/static/upload/images", file_name)
            file_path = os.path.join(current_app.root_path, "static/upload/images",
                                     file_name)  # f.filename是你刚刚在浏览器选择的那个上传的图片的名字
            f.save(file_path)  # a/b/c/123.png

            # 将这个新闻内容添加到数据库中
            try:
                news = News()
                news.title = title
                news.category_id = category
                news.source = "个人发布"
                news.digest = digest
                news.content = content
                news.user = g.user
                news.index_image_url = local_file_path
                news.status = 1  # 表示刚刚的这个新闻正在审核

                db.session.add(news)
                db.session.commit()

                ret = {
                    "errno": 0,
                    "errmsg": "保存成功"
                }
            except Exception as ret:
                print("保存新闻失败 ....", ret)
                ret = {
                    "errno": 0,
                    "errmsg": "新闻保存失败"
                }

            return jsonify(ret)


@user_blu.route("/user_news_list")
@login_user_data
def user_news_list():
    # 新闻列表
    # 获取当前ID发布的新闻关联
    # 获取用户当前查看的页码
    page = request.args.get("page", 1)

    # 页码中显示多少个页数
    paginate = g.user.news.paginate(int(page), 4, False)

    news = [x.to_news_list_dict() for x in paginate.items]
    print(news)

    return render_template("index/user_news_list.html", news=news, paginate=paginate)
