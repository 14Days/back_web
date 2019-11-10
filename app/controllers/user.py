from flask import Blueprint, request, current_app, session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import add_user, check_user, delete_user
from app.utils.warp import success_warp, fail_warp
from app.utils.errors import errors
from app.utils.md5 import encode_md5

user_page = Blueprint('user', __name__, url_prefix='/user')


@user_page.route('/add', methods=['POST'])
def add():
    user_id = session['user_id']
    user_type = session['type']
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username is None or username == '' or \
            password is None or password == '':
        current_app.logger.error('params error %s', str({
            'username': username,
            'password': password,
            'parent_id': user_id
        }))
        return fail_warp(errors['101']), 400

    try:
        check_user(username)
        add_user(username, encode_md5(password), user_id, user_type + 1)
        current_app.logger.info('add user success %s', str({
            'parent': user_id,
            'username': username
        }))
        return success_warp('add success')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(errors['501']), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@user_page.route('/delete', methods=['POST'])
def delete_users():
    user_id = session['user_id']
    data = request.json.get('user_id')
    if type(data) != list:
        current_app.logger.error('params error %s', str({
            'body': data
        }))
        return fail_warp(errors['101']), 400

    try:
        delete_user(data, user_id)
        current_app.logger.info('delete user success %s', str({
            'parent': user_id,
            'username': data
        }))
        return success_warp('delete success')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(errors['501']), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
