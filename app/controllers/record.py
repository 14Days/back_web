import re
import datetime
from flask import Blueprint, request, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models.record import RecordBuild
from app.utils.auth import auth_require, Permission
from app.utils.warp import success_warp, fail_warp
from app.utils.errors import errors

record_page = Blueprint('record', __name__, url_prefix='/record')


@record_page.route('', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def record_get():
    data = request.args
    start = data.get('start')
    end = data.get('end')

    if start is None or re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}', start) is None or \
            end is None or re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}', end) is None:
        current_app.logger.error('record error %s', str({
            'start': start,
            'end': end
        }))
        return fail_warp(errors['101'])

    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    end = datetime.datetime.strptime(end, '%Y-%m-%d')

    try:
        temp = RecordBuild(start, end).get_res()
        current_app.logger.info('record info %s', str({
            'data': temp
        }))
        return success_warp(temp)
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
