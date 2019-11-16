from flask import Blueprint, request, session
from app.models.notice import GetNotice
from app.utils.warp import success_warp, fail_warp
from app.utils.auth import auth_require, Permission

notice_page = Blueprint('notice', __name__, url_prefix='/notice')


@notice_page.route('', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def notice_get():
    user_id = session['user_id']
    role = session['type']
    limit = request.args.get('limit') if request.args.get('limit') is not None else 20
    page = request.args.get('page') if request.args.get('page') is not None else 0
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    notice_type = request.args.get('type')

    count, res = GetNotice(role).get_res(user_id, limit, page, start_time, end_time, notice_type)

    return success_warp({
        'count': count,
        'notice': res
    })
