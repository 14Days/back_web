from flask import Blueprint, request, current_app, session
from sqlalchemy.exc import SQLAlchemyError
from app.utils.warp import success_warp, fail_warp
from app.utils.errors import errors
from app.models.login import confirm_user
from app.utils.md5 import encode_md5

login_page = Blueprint('login', __name__, url_prefix='/login')


@login_page.route('', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username is None or username == '' or \
            password is None or password == '':
        current_app.logger.error('params error')
        return 400, fail_warp(errors['101'])

    try:
        res = confirm_user(username, encode_md5(password))
        if res is not None:
            session['user_id'] = res.id
            return success_warp({
                'type': res.role
            })
        else:
            current_app.logger.error('login fail')
            return fail_warp('login fail')
    except SQLAlchemyError as e:
        current_app.logger.error('query error', e)
        return fail_warp(errors['301'])
