from flask import Blueprint, request, current_app, session
from sqlalchemy.exc import SQLAlchemyError
from app.utils.warp import success_warp, fail_warp
from app.utils.errors import errors
from app.models.login import confirm_user
from app.utils.md5 import encode_md5

login_page = Blueprint('login', __name__, url_prefix='/login')


@login_page.route('', methods=['POST'])
def login_post():
    """
    用户登陆
    :return:
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username is None or username == '' or \
            password is None or password == '':
        current_app.logger.error('params error %s', str({
            'username': username,
            'password': password
        }))
        return fail_warp(errors['101']), 400

    try:
        res = confirm_user(username, encode_md5(password))
        if res is not None:
            session['user_id'] = res.id
            session['type'] = res.role
            current_app.logger.info('login success %s', str({
                'username': username,
                'type': res.role
            }))
            return success_warp({
                'type': res.role,
                'user_id': res.id
            })
        else:
            current_app.logger.error('login fail %s', str({
                'username': username,
                'password': password
            }))
            return fail_warp(errors['401']), 400
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(errors['501']), 500


@login_page.route('', methods=['DELETE'])
def login_delete():
    """
    退出登陆
    :return:
    """
    user_id = session.get('user_id')
    session.clear()

    current_app.logger.info('logout success %s', str({
        'user_id': user_id
    }))
    return success_warp('logout success')
