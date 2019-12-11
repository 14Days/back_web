from flask import Blueprint, request, session, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models.gallery import post_dir, get_dir
from app.utils.auth import auth_require, Permission
from app.utils.warp import fail_warp, success_warp
from app.utils.errors import errors

gallery_page = Blueprint('gallery', __name__, url_prefix='/gallery')


@gallery_page.route('', methods=['GET'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def get_gallery():
    user_id = session['user_id']
    data = request.args
    limit = int(data.get('limit')) if data.get('limit') is not None else 20
    page = int(data.get('page')) if data.get('page') is not None else 0

    try:
        dirs = get_dir(user_id, limit, page)
        current_app.logger.info('gallery info %s', str({
            'dirs': dirs,
        }))
        return success_warp(dirs)
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@gallery_page.route('', methods=['POST'])
@auth_require(Permission.ADMIN | Permission.DESIGNER)
def post_gallery():
    user_id = session['user_id']
    data = request.json
    name = data.get('name')

    if name is None:
        current_app.logger.error('gallery info %s', str({
            'name': name,
        }))
        return fail_warp(errors['101']), 400

    try:
        id = post_dir(name, user_id)
        current_app.logger.info('gallery info %s', str({
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
def delete_gallery(dir_id):
    # TODO 删除分类列表
    pass
