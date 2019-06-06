from flask import request, render_template, session, make_response, jsonify

from app import db
from app.models.models import User
from . import passport_blu


@passport_blu.route("/register", methods=["POST"])
def register():
    # 查看什么方式获取数据
    # js中获取数据的方式是jsonify，所有用test = request.json可以看到用户输入的数据
    # print("---------")
    # test = request.json
    # print(test)
    # print("-----2----")
    # print(request.form)  # 获取的数据为空ImmutableMultiDict([])

    # 明确获取数据的方式，然后在进行下一步获取
    mobile = request.json.get("mobile")  # 手机号码
    image_code = request.json.get("image_code")  # 验证码图片
    password = request.json.get("password")  # 用户输入密码
    # 获取验证码在session中存储的数据
    captcha = session.get('captcha')
    # print(mobile,image_code,password)
    if not all([mobile, image_code, password]):
        ret = {
            "errno": 1002,
            "errmsg": "缺少参数"
        }

        return jsonify(ret)

    # 将获取出来的验证码进行判断
    if image_code.lower() != captcha.lower():
        print(image_code, captcha)
        ret = {
            "errno": 1001,
            "errmsg": "验证码不正确"
        }

        return jsonify(ret)

    # 数据库添加
    user = User()
    if user:
        user.nick_name = mobile  # 用户姓名
        user.mobile = mobile  # 手机号
        user.password_hash = password  # 密码
        # commit 到数据库
        try:
            # 成功后提交到数据库，并携带session
            db.session.add(user)
            db.session.commit()  # 提交到数据库
            session["user_id"] = user.id
            session["nick_name"] = user.nick_name
        except Exception as ret:
            db.session.rollback()  # 提交不完成就回滚

        ret = {
            "errno": 0,
            "errmsg": "注册成功"
        }

        return jsonify(ret)


@passport_blu.route("/login", methods=["POST"])
def login():
    # 获取用户数据
    mobile = request.json.get("mobile")
    password = request.json.get("password")

    # 判断是否为空
    if not mobile and password:
        ret = {
            "errno": 2001,
            "errmsg": "缺少参数"
        }

        return jsonify(ret)

    # 判断用户输入的于数据是否成立
    user = db.session.query(User).filter(User.mobile == mobile, User.password_hash == password).first()
    if not user:
        # 不成立的话
        ret = {
            "errno": 2002,
            "errmsg": "用户名或密码不正确"

        }

        return jsonify(ret)

    # 成立的话使用session部分保存标记成功
    session["user_id"] = user.id
    session["nick_name"] = mobile
    ret = {
            "errno": 0,
            "errmsg": "登录成功"

            }

    return jsonify(ret)


@passport_blu.route("/logout", methods=["POST"])
def logout():
    # 点击退出清除session
    session.clear()

    ret = {
        "errno": 0,
        "errmsg": "退出成功"
    }

    return jsonify(ret)


# 请求的是main.js中"/passport/image_code?code_id=" + imageCodeId;
# 验证码试图函数
@passport_blu.route("/image_code")
def image_code():
    from app.utils.captcha.captcha import captcha

    # 生成验证码
    # hash值  验证码值  图片内容
    name, text, image = captcha.generate_captcha()

    # print("注册时的验证码为：", name, text, images)  # hash值  验证码值  图片内容

    # 将生成的图片验证码值作为value，存储到session中
    session["captcha"] = text  # 通过session的方式将刚刚生成的图片验证码的值，进行存储，以便在登录的时候进行验证 图片验证码是否输入正确

    # 返回响应内容
    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'images/jpg'
    return resp
