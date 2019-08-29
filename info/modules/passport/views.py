from flask import request, abort, current_app, make_response, session, jsonify

from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport
from info import redis_store, constants, mail, db
from info.utils.mail.mail import send_mail

import re
import random


def send_mail_code(to, **kwargs):
    send_mail(mail, to, "注册验证码", 'emails/sms', **kwargs)


@passport.route('/image_code')
def image_code():
    image_code_id = request.args.get("imageCodeId", None)
    if not image_code_id:
        abort(404)
    name, text, image = captcha.generate_captcha()
    try:
        redis_store.set("ImageCodeId:" + image_code_id, text, ex=constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response


def check_register_params(request):
    name = request.json.get('username', None)
    email_address = request.json.get('email', None)
    image_code = request.json.get("imageCode", None)
    pass


@passport.route('/mail', methods=['POST'])
def send_email_code():
    params_dict = request.json
    current_app.logger.info(params_dict)
    name = request.json.get('username', None)
    email_address = request.json.get('email', None)

    if not re.match(r'[0-9a-zA-Z]{8,16}', name):
        return jsonify(errno=RET.PARAMERR, errmsg="用户名格式错误")
    if not re.match(r'^[0-9a-zA-Z)]{0,19}@[0-9]{1,13}\.com', email_address):
        return jsonify(errno=RET.PARAMERR, errmsg="邮箱格式错误")

    if name is None and email_address is None:
        return jsonify(code=4000, msg="参数错误")
    image_code = request.json.get("image_code", None)
    image_code_id = request.json.get("image_code_id", None)
    try:
        redis_image_code = redis_store.get("ImageCodeId:" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据查询失败")
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")
    if image_code.upper() != redis_image_code.upper():
        return jsonify(code=RET.DATAERR, errmsg="验证码输入错误")
    email_code_str = '{}'.format(random.randint(0, 999999))
    current_app.logger.info("邮箱:%s的验证码是%s" % (email_address, email_code_str))
    try:
        redis_store.set("EmailCode:" + email_address, email_code_str, ex=constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.log.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据添加失败")
    send_mail_code(email_address, name=name, code=email_code_str)
    return jsonify(errno=RET.OK, msg="发送成功")


@passport.route('/v2/register', methods=['POST'])
def registeV2():
    params_dict = request.json
    username, email, email_code, password = params_dict.get("username", "email", "email_code", "password")
    current_app.loger.info(params_dict)

    if not all([username, email, email_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if not re.match(r'[0-9a-zA-Z]{8,16}', username):
        return jsonify(errno=RET.PARAMERR, errmsg="用户名格式错误")
    if not re.match(r'^[0-9a-zA-Z)]{0,19}@[0-9]{1,13}\.com', email):
        return jsonify(errno=RET.PARAMERR, errmsg="邮箱格式错误")
    if not re.match(r'[0-9a-zA-Z_]{6,15}', password):
        return jsonify(errno=RET.PARAMERR, errmsg="密码格式错误")
    try:
        real_email_code = redis_store.get("EmailCode:" + email)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据查询失败")
    if not real_email_code:
        return jsonify(errno=RET.NODATA, errmsg="邮箱验证码已过期")
    if real_email_code != email_code:
        return jsonify(errno=RET.PARAMERR, errmsg="邮箱验证码输入错误")

    user = User()
    user.nick_name = username
    user.email = email
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['email'] = user.email


@passport.route('/login', methods=['POST'])
def login():
    pass
