import os
import pathlib
from flask import Blueprint, request, current_app, session
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import add_user, \
    check_user, \
    delete_user, \
    get_user, \
    get_user_detail, \
    save_avatar, \
    change_user_info
from app.utils.warp import success_warp, fail_warp
from app.utils.errors import errors
from app.utils.md5 import encode_md5, file_md5

user_page = Blueprint('user', __name__, url_prefix='/user')


class User(MethodView):
    @staticmethod
    def get(this_user: int):
        """
        得到所有用户与指定用户信息
        :return:
        """
        user_id = session['user_id']
        if this_user is None:
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
        else:
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

    @staticmethod
    def post():
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

    @staticmethod
    def delete():
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

    @staticmethod
    def put(this_user: int):
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
            current_app.logger.info('params error %s', str({
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


user_view = User.as_view('user_api')
user_page.add_url_rule('', defaults={'this_user': None}, view_func=user_view, methods=['GET'])
user_page.add_url_rule('', view_func=user_view, methods=['POST'])
user_page.add_url_rule('/<int:this_user>', view_func=user_view, methods=['GET', 'PUT'])
user_page.add_url_rule('', view_func=user_view, methods=['DELETE'])


class Upload(MethodView):
    _UPLOAD_FOLDER = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent.parent, 'avatar')
    _ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Upload._ALLOWED_EXTENSIONS

    @staticmethod
    def post():
        f = request.files.get('avatar')
        # 校验存在性
        if f is None:
            current_app.logger.error('params error')
            return fail_warp(errors['101']), 400
        if not Upload.allowed_file(f.filename):
            current_app.logger.error('file error')
            return fail_warp(errors['102']), 400

        file_path = pathlib.Path.joinpath(Upload._UPLOAD_FOLDER, f.filename)
        f.save(str(file_path))

        # 文件重命名
        name = file_md5(file_path) + '.' + f.filename.rsplit('.', 1)[1].lower()
        os.rename(
            str(file_path),
            str(pathlib.Path.joinpath(Upload._UPLOAD_FOLDER, name))
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


upload_view = Upload.as_view('upload_api')
user_page.add_url_rule('/avatar', view_func=upload_view, methods=['POST'])
