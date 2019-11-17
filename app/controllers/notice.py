from flask import Blueprint, request, session, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models.notice import GetNotice
from app.utils.warp import success_warp, fail_warp
from app.utils.auth import auth_require, Permission
from app.utils.errors import errors

notice_page = Blueprint('notice', __name__, url_prefix='/notice')


@notice_page.route('', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def notice_get():
    """
    获取通知
    :return:
    """
    user_id = session['user_id']
    role = session['type']
    limit = request.args.get('limit') if request.args.get('limit') is not None else 20
    page = request.args.get('page') if request.args.get('page') is not None else 0
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    notice_type = request.args.get('type')

    try:
        count, res = GetNotice(role).get_all_res(user_id, limit, page, start_time, end_time, notice_type)
        current_app.logger.info({
            'count': count,
            'notice': res
        })
        return success_warp({
            'count': count,
            'notice': res
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@notice_page.route('/<int:notice_id>', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def notice_get_detail(notice_id: int):
    """
    获取通知详情
    :param notice_id:
    :return:
    """
    user_id = session['user_id']
    role = session['type']
    try:
        res = GetNotice(role).get_detail_res(user_id, notice_id)
        current_app.logger.info({
            'notice': res
        })
        return success_warp(res)
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@notice_page.route('', methods=['POST'])
@auth_require(Permission.ROOT | Permission.ADMIN)
def notice_post():
    """
    添加通知
    :return:
    """
    user_id = session['user_id']
    role = session['type']
    data = request.json

    title = data.get('title')
    content = data.get('content')
    notice_type = data.get('type')
    is_top = data.get('is_top')

    if title is None or title == '' or \
            notice_type is None or is_top is None:
        current_app.logger.error('params error %s', str({
            'title': title,
            'content': content,
            'type': notice_type,
            'is_top': is_top,
            'user_id': user_id
        }))
        return fail_warp(errors['101']), 400

    try:
        GetNotice(role).post_notice(title, content, is_top, notice_type, user_id)
        current_app.logger.info({
            'title': title,
            'content': content,
            'type': notice_type,
            'is_top': is_top,
            'user_id': user_id
        })
        return success_warp('add notice success')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
