from flask import Blueprint, session, request, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models.comment import CommentFactory
from app.utils.auth import auth_require, Permission
from app.utils.errors import errors
from app.utils.warp import success_warp, fail_warp

comment_page = Blueprint('comment', __name__, url_prefix='/comment')


@comment_page.route('', methods=['DELETE'])
@auth_require(Permission.ROOT | Permission.ADMIN)
def delete_comment():
    user_id = session['user_id']
    role = session['type']
    data = request.json
    level = data.get('level')
    comment_id = data.get('comment_id')

    if (level != 1 and level != 2) or type(comment_id) != int:
        current_app.logger.error('params error %s', str({
            'comment_id': comment_id,
            'level': level,
            'user_id': user_id
        }))
        return fail_warp(errors['101']), 400

    try:
        CommentFactory(role, level).delete_item(comment_id, user_id)
        current_app.logger.info({
            'comment_id': comment_id,
            'level': level,
            'user_id': user_id
        })
        return success_warp('删除成功')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
