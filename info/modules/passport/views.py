from flask import request, abort, current_app, make_response, render_template
from info.utils.captcha.captcha import captcha
from . import passport
from info import redis_store, constants, mail
from info.utils.mail.mail import send_mail


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


@passport.route('/sms', methods=['POST'])
def get_sms():
    pass


@passport.route('/mail', methods=['POST'])
def send_email_code():
    name = request.json.get('username')
    email_address = request.json.get('email')
    send_mail_code(email_address, name=name,code=1234)
    return 'ok'
