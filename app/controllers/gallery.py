from flask import Blueprint, session

gallery_page = Blueprint('gallery', __name__, url_prefix='/gallery')


@gallery_page.route('', methods=['GET'])
def get_gallery():
    # TODO 获取所有图片
    pass


@gallery_page.route('', methods=['DELETE'])
def delete_gallery():
    # TODO 删除图片
    pass
