import datetime
from app.models import db, session_commit
from app.models.model import Dir, Img
from app.utils.errors import errors


def get_dir(user_id: int, limit: int, page: int):
    """
    获取所有文件夹
    """
    base = Dir.query. \
        filter(Dir.user_id == user_id). \
        filter(Dir.delete_at.is_(None)). \
        order_by(Dir.name)
    count = base.count()
    dirs = base. \
        limit(limit).offset(limit * page). \
        all()
    temp = []
    for dirname in dirs:
        temp.append({
            'id': dirname.id,
            'name': dirname.name
        })

    return count, temp


def get_dir_detail(dir_id: int, limit: int, page: int, user_id: int):
    """
    获取文件夹内容
    """
    base = Img.query. \
        filter(Img.dir_id == dir_id). \
        filter(Img.user_id == user_id). \
        filter(Img.delete_at.is_(None))

    count = base.count()
    images = base. \
        limit(limit).offset(limit * page). \
        all()

    temp = []
    for item in images:
        temp.append({
            'uploader': item.user.nickname,
            'img_id': item.id,
            'file_id': dir_id,
            'upload_time': item.create_at.strftime('%Y-%m-%d'),
            'count': item.type,
            'name': item.name
        })

    return count, temp


def post_dir(name: str, user_id: int):
    dirname = Dir(
        name=name,
        user_id=user_id
    )
    db.session.add(dirname)
    session_commit()
    return dirname.id


def delete_dir(dir_id: int, user_id: int):
    """
    删除文件夹
    """
    dirname = Dir.query. \
        filter(Dir.id == dir_id). \
        filter(Dir.user_id == user_id). \
        filter(Dir.delete_at.is_(None)). \
        first()

    if dirname is None:
        raise RuntimeError(errors['501'])

    for item in dirname.images:
        item.dir_id = 0

    dirname.delete_at = datetime.datetime.now()
    session_commit()


def put_dir(dir_id: int, new_name: str, user_id: int):
    """
    修改文件夹
    """
    dirname = Dir.query. \
        filter(Dir.id == dir_id). \
        filter(Dir.user_id == user_id). \
        filter(Dir.delete_at.is_(None)). \
        first()

    if dirname is None:
        raise RuntimeError(errors['501'])

    dirname.name = new_name
    session_commit()


def delete_dir_img(img_id: int, user_id: int):
    img = Img.query. \
        filter(Img.id == img_id). \
        filter(Img.user_id == user_id). \
        filter(Img.delete_at.is_(None)). \
        first()

    if img is None:
        raise RuntimeError(errors['501'])

    if img.type != 0:
        raise RuntimeError(errors['502'])

    img.delete_at = datetime.datetime.now()
