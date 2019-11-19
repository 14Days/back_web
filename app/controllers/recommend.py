from flask import Blueprint, request, session, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models.recommend import save_img
from app.utils.auth import auth_require, Permission
from app.utils.img import allowed_file, deal_img
from app.utils.warp import success_warp, fail_warp
from app.utils.errors import errors

recommend_page = Blueprint('recommend', __name__, url_prefix='/img')


@recommend_page.route('', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def recommend_get():
    pass


@recommend_page.route('', methods=['POST'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def recommend_post():
    pass


@recommend_page.route('/upload', methods=['POST'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def upload_img():
    f = request.files.get('img')
    # 校验存在性
    if f is None:
        current_app.logger.error('params error')
        return fail_warp(errors['101']), 400
    if not allowed_file(f.filename):
        current_app.logger.error('file error')
        return fail_warp(errors['102']), 400

    name = deal_img('img', f)

    try:
        img = save_img(name)
        current_app.logger.info('delete user success %s', str({
            'avatar_id': img.id,
        }))
        return success_warp({
            'img_id': img.id
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(errors['501']), 500
