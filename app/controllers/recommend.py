from flask import Blueprint, request, session, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models.recommend import save_img, GetRecommend
from app.utils.auth import auth_require, Permission
from app.utils.img import allowed_file, deal_img
from app.utils.warp import success_warp, fail_warp
from app.utils.errors import errors

recommend_page = Blueprint('recommend', __name__, url_prefix='/img')
# TODO 逐个核对适应新逻辑


@recommend_page.route('', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def recommend_get():
    """
    获得推荐消息
    :return:
    """
    user_id = session['user_id']
    role = session['type']
    data = request.args
    limit = int(data.get('limit')) if data.get('limit') is not None else 20
    page = int(data.get('page')) if data.get('page') is not None else 0
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    nickname = data.get('nick_time')
    content = data.get('content')

    try:
        count, res = GetRecommend(role).get_recommend(limit, page, start_time, end_time, nickname, content, user_id)
        current_app.logger.info({
            'count': count,
            'res': res
        })
        return success_warp({
            'count': count,
            'res': res
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@recommend_page.route('/<int:recommend_id>', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def recommend_get_detail(recommend_id: int):
    """
    获取评论详情
    :param recommend_id:
    :return:
    """
    user_id = session['user_id']
    role = session['type']

    try:
        res = GetRecommend(role).get_recommend_detail(user_id, recommend_id)
        current_app.logger.info({
            'recommend': res
        })
        return success_warp(res)
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@recommend_page.route('', methods=['POST'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def recommend_post():
    """
    发送推荐消息
    :return:
    """
    user_id = session['user_id']
    role = session['type']
    data = request.json
    content = data.get('content')
    img = data.get('img')

    if img is None or type(img) != list:
        current_app.logger.error('recommend info %s', str({
            'content': content,
            'img': img
        }))
        return fail_warp(errors['101']), 400

    try:
        GetRecommend(role).post_recommend(content, img, user_id)
        current_app.logger.info('recommend info %s', str({
            'content': content,
            'img': img,
            'user_id': user_id
        }))
        return success_warp('add recommend success')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@recommend_page.route('/upload', methods=['POST'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def upload_img():
    """
    上传推荐消息图片
    :return:
    """
    user_id = session['user_id']
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
        img = save_img(name, user_id)
        current_app.logger.info('delete user success %s', str({
            'avatar_id': img.id,
        }))
        return success_warp({
            'img_id': img.id
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(errors['501']), 500


@recommend_page.route('/<int:recommend_id>', methods=['PUT'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def recommend_put(recommend_id):
    user_id = session['user_id']
    role = session['type']
    data = request.json
    content = data.get('content')
    new_img_id = data.get('new_img_id')
    old_img_id = data.get('old_img_id')

    if new_img_id is None or type(new_img_id) != list or \
            old_img_id is None or type(old_img_id) != list:
        current_app.logger.error('put recommend info %s', str({
            'content': content,
            'new_img': new_img_id,
            'old_img': old_img_id
        }))
        return fail_warp(errors['101']), 400

    try:
        GetRecommend(role).put_recommend(content, new_img_id, old_img_id, user_id, recommend_id)
        current_app.logger.info('put recommend %s', str({
            'content': content,
            'new_img': new_img_id,
            'old_img': old_img_id,
            'recommend': recommend_id
        }))
        return success_warp('put recommend success')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500


@recommend_page.route('', methods=['DELETE'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def recommend_delete():
    user_id = session['user_id']
    role = session['type']
    recommend_ids = request.json.get('recommend_id')
    if recommend_ids is None or type(recommend_ids) != list:
        current_app.logger.error('recommend id %s', str({
            'id': recommend_ids
        }))
        return fail_warp(errors['101']), 400

    try:
        GetRecommend(role).delete_recommend(user_id, recommend_ids)
        current_app.logger.info('recommend info %s', str({
            'user_id': user_id,
            'recommend_ids': recommend_ids
        }))
        return success_warp('add recommend success')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
    except RuntimeError as e:
        current_app.logger.error(e)
        return fail_warp(e.args[0]), 500
