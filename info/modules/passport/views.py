from flask import request, abort, current_app, make_response, render_template, jsonify
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport
from info import redis_store, constants, mail
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
    name = request.json.get('username', None)
    if not re.match(r'[0-9a-zA-Z]{8,16}', name):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    email_address = request.json.get('email', None)
    if not re.match(r'[0-9a-zA-Z]{0,19}@[0-9a-zA-Z]{1,13}\.com]', email_address):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if name is None and email_address is None:
        return jsonify(code=4000, msg="参数错误")
    image_code = request.json.get("image_code", None)
    image_code_id = request.json.get("image_code_id", None)
    # redis_image_code = 0
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
    current_app.logger.info("邮箱:{}的验证码是{}".format(email_address, email_code_str))
    try:
        redis_store.set("EmailCode:" + email_address, email_code_str, ex=constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.log.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据添加失败")
    send_mail_code(email_address, name=name, code=email_code_str)
    return jsonify(errno=RET.OK, msg="发送成功")


@passport.route('/register', methods=['POST'])
def register():
    pass
