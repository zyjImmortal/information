from flask import Blueprint

passport = Blueprint('passport', __name__, url_prefix='/passport')


from . import views