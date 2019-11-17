import os
import pathlib
from flask import Blueprint, request, current_app, session
from app.utils.auth import auth_require, Permission
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import add_user, \
    check_user, \
    delete_user, \
    get_user, \
    get_user_detail, \
    save_avatar, \
    change_user_info, \
    change_password
from app.utils.warp import success_warp, fail_warp
from app.utils.errors import errors
from app.utils.md5 import encode_md5, file_md5
from app.utils.compression import compress

user_page = Blueprint('user', __name__, url_prefix='/user')


@user_page.route('', methods=['GET'])
@auth_require(Permission.ADMIN | Permission.ROOT)
def user_get_all_user():
    """
    得到所有用户信息
    :return:
    """
    user_id = session['user_id']
    username = request.args.get('username')

    try:
        user, count = get_user(user_id, username)
        current_app.logger.info('user info %s', str({
            'user': user,
            'total': count
        }))
        return success_warp({
            'user': user,
            'total': count
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(errors['501']), 500


@user_page.route('/<int:this_user>', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def user_get_detail(this_user):
    """
    得到某一用户的信息
    :param this_user:
    :return:
    """
    user_id = session['user_id']
    try:
        user = get_user_detail(user_id, this_user)
        current_app.logger.info('user detail %s', str(user))
        return success_warp(user)
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(errors['501']), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@user_page.route('', methods=['POST'])
@auth_require(Permission.ROOT | Permission.ADMIN)
def user_post():
    """
    添加用户
    :return:
    """
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


@user_page.route('', methods=['DELETE'])
@auth_require(Permission.ROOT | Permission.ADMIN)
def user_delete():
    """
    删除用户
    :return:
    """
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


@user_page.route('/<int:this_user>', methods=['PUT'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def user_put(this_user):
    """
    修改用户信息
    :param this_user:
    :return:
    """
    user_id = session['user_id']
    nickname = request.json.get('nickname')
    sex = request.json.get('sex')
    email = request.json.get('email')
    phone = request.json.get('phone')
    avatar = request.json.get('avatar')

    # 一级参数检验
    if nickname is None or nickname == '' or \
            sex is None or sex == '' or \
            email is None or phone is None or \
            type(avatar) != dict or this_user is None:
        current_app.logger.error('params error %s', str({
            'nickname': nickname,
            'sex': sex,
            'email': email,
            'phone': phone,
            'avatar': avatar
        }))
        return fail_warp(errors['101']), 400

    old_avatar, new_avatar = avatar.get('old_id'), avatar.get('new_id')

    if old_avatar is None or new_avatar is None:
        current_app.logger.error('params error %s', str({
            'avatar': avatar
        }))
        return fail_warp(errors['101']), 400

    try:
        change_user_info(user_id, this_user, nickname, sex, email, phone, avatar)
        current_app.logger.info('change user info success %s', str({
            'nickname': nickname,
            'sex': sex,
            'email': email,
            'phone': phone,
            'avatar': avatar
        }))
        return success_warp('update success')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@user_page.route('/avatar', methods=['POST'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def upload_post():
    """
    上传头像
    :return:
    """
    _UPLOAD_FOLDER = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent.parent, 'avatar')
    _ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in _ALLOWED_EXTENSIONS

    f = request.files.get('avatar')
    # 校验存在性
    if f is None:
        current_app.logger.error('params error')
        return fail_warp(errors['101']), 400
    if not allowed_file(f.filename):
        current_app.logger.error('file error')
        return fail_warp(errors['102']), 400

    file_path = pathlib.Path.joinpath(_UPLOAD_FOLDER, f.filename)
    f.save(str(file_path))
    # 压缩图片
    new_path = compress(str(file_path))

    # 文件重命名
    name = file_md5(new_path) + '.jpg'
    os.rename(
        str(file_path),
        str(pathlib.Path.joinpath(_UPLOAD_FOLDER, name))
    )

    try:
        avatar = save_avatar(name)
        current_app.logger.info('delete user success %s', str({
            'avatar_id': avatar.id,
        }))
        return success_warp({
            'avatar_id': avatar.id
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(errors['501']), 500


@user_page.route('/password/<int:this_user>', methods=['PUT'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def password_put(this_user):
    """
    修改密码
    :param this_user:
    :return:
    """
    user_id = session['user_id']
    data = request.json
    new_password = data.get('new_password')
    old_password = data.get('old_password')

    if user_id == this_user:
        if new_password is None or new_password == '' or \
                old_password is None or old_password == '':
            current_app.logger.error('params error %s', str({
                'new_password': new_password,
                'old_password': old_password
            }))
            return fail_warp(errors['101']), 400
    else:
        if new_password is None or new_password == '':
            current_app.logger.error('params error %s', str({
                'new_password': new_password,
                'old_password': old_password
            }))
            return fail_warp(errors['101']), 400

    try:
        change_password(user_id, this_user, encode_md5(new_password), encode_md5(old_password))
        current_app.logger.info('change password success %s', str({
            'this_user': this_user
        }))
        return success_warp('update success')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
