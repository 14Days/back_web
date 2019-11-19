from flask import Blueprint, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models.params import get_tags
from app.utils.warp import success_warp, fail_warp

params_page = Blueprint('params', __name__, url_prefix='/params')


@params_page.route('/style', methods=['GET'])
def style_get():
    try:
        data = get_tags()
        current_app.logger.info('return style success')
        return success_warp(data)
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
