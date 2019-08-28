from flask import request, abort, current_app, make_response, render_template, jsonify
from info.utils.captcha.captcha import captcha
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
        redis_store.set("ImageCodeId:" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
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
    re.search(r'[0-9a-zA-Z]{8,16}', name)

    email_address = request.json.get('email', None)
    if name is None and email_address is None:
        return jsonify(code=4000, msg="参数错误")
    image_code = request.json.get("imageCode", None)
    image_code_id = request.json.get("imageCodeId", None)
    redis_image_code = 0
    try:
        redis_image_code = redis_store.get("ImageCodeId:" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    if image_code != redis_image_code:
        return jsonify(code=4000, msg="传递的image_code错误")
    email_code = random.randint(0, 9999)
    try:
        redis_store.set("EmailCode:" + email_address + ":" + image_code_id + ":" + email_code)
    except Exception as e:
        current_app.log.error(e)
        abort(500)
    send_mail_code(email_address, name=name, code=email_code)
    return jsonify(code=1000, msg="发送成功")


@passport.route('/register', methods=['POST'])
def register():
    pass
