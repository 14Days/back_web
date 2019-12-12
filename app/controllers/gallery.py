from flask import Blueprint, request, session, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models.gallery import post_dir, get_dir, delete_dir, put_dir, get_dir_detail, delete_dir_img, put_dir_img_move
from app.utils.auth import auth_require, Permission
from app.utils.warp import fail_warp, success_warp
from app.utils.errors import errors

gallery_page = Blueprint('gallery', __name__, url_prefix='/gallery')


@gallery_page.route('', methods=['GET'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def get_gallery():
    """
    获取分类列表
    """
    user_id = session['user_id']
    data = request.args
    limit = int(data.get('limit')) if data.get('limit') is not None else 20
    page = int(data.get('page')) if data.get('page') is not None else 0

    try:
        count, dirs = get_dir(user_id, limit, page)
        current_app.logger.info('gallery info %s', str({
            'dirs': dirs,
            'count': count
        }))
        return success_warp({
            'count': count,
            'dirs': dirs
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@gallery_page.route('/<int:gallery_id>', methods=['GET'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def get_gallery_detail(gallery_id):
    """
    获取分类详情
    """
    user_id = session['user_id']
    data = request.args
    limit = int(data.get('limit')) if data.get('limit') is not None else 20
    page = int(data.get('page')) if data.get('page') is not None else 0

    try:
        count, images = get_dir_detail(gallery_id, limit, page, user_id)
        current_app.logger.info('gallery detail info %s', str({
            'count': count,
            'images': images
        }))
        return success_warp({
            'count': count,
            'images': images
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)


@gallery_page.route('', methods=['POST'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def post_gallery():
    """
    添加分类
    """
    user_id = session['user_id']
    data = request.json
    name = data.get('name')

    if name is None or name == '':
        current_app.logger.error('gallery info %s', str({
            'name': name,
        }))
        return fail_warp(errors['101']), 400

    try:
        id = post_dir(name, user_id)
        current_app.logger.info('gallery post %s', str({
            'name': name,
            'id': id
        }))
        return success_warp({
            'id': id
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@gallery_page.route('/<int:dir_id>', methods=['DELETE'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def delete_gallery(dir_id: int):
    """
    删除分类
    """
    user_id = session['user_id']

    try:
        delete_dir(dir_id, user_id)
        current_app.logger.info('gallery delete %s', str({
            'id': dir_id
        }))
        return success_warp('删除成功')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@gallery_page.route('/<int:dir_id>', methods=['PUT'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def put_gallery(dir_id: int):
    """
    修改分类名称
    """
    user_id = session['user_id']

    data = request.json
    new_name = data.get('name')
    if new_name is None or new_name == '':
        current_app.logger.error('gallery info %s', str({
            'name': new_name,
        }))
        return fail_warp(errors['101']), 400

    try:
        put_dir(dir_id, new_name, user_id)
        current_app.logger.info('gallery put %s', str({
            'id': dir_id,
            'new_name': new_name
        }))
        return success_warp('修改成功')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@gallery_page.route('/img', methods=['DELETE'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def delete_img():
    user_id = session['user_id']
    img_id = request.json.get('img_id')

    if img_id is None or img_id == '':
        current_app.logger.error('img delete %s', str({
            'img_id': img_id
        }))
        return fail_warp(errors['101']), 400

    try:
        delete_dir_img(img_id, user_id)
        current_app.logger.info('img delete %s', str({
            'id': img_id,
            'user': user_id
        }))
        return success_warp('删除成功')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@gallery_page.route('/img/move', methods=['PUT'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def put_move_img():
    user_id = session['user_id']
    data = request.json
    img_id = data.get('img_id')
    file_id = data.get('file_id')

    if type(img_id) != int or type(file_id) != int:
        current_app.logger.error('img move %s', str({
            'img_id': img_id,
            'file_id': file_id
        }))
        return fail_warp(errors['101']), 400

    try:
        put_dir_img_move(img_id, file_id, user_id)
        current_app.logger.info('img delete %s', str({
            'id': img_id,
            'file_id': file_id,
            'user': user_id
        }))
        return success_warp('移动成功')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
