from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_mail import Mail
import logging
from logging.handlers import RotatingFileHandler
from config import config

db = SQLAlchemy()
mail = Mail()


def setup_log(config_name):
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_log_handler)


redis_store = None  # type:StrictRedis


def create_app(config_name):
    setup_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    mail.init_app(app)
    global redis_store
    # decode_responses设置为True，自动将字节数据解析
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT, decode_responses=True)
    Session(app)  # 指定session存储位置，
    # CSRFProtect(app)

    # app.json_encoder

    from info.modules.index import index_blu
    from info.modules.passport import passport
    app.register_blueprint(index_blu)
    app.register_blueprint(passport)
    return app
