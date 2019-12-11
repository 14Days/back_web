from app.models import db, session_commit
from app.models.model import Dir


def get_dir(user_id: int, limit: int, page: int):
    dirs = Dir.query. \
        filter(Dir.user_id == user_id). \
        filter(Dir.delete_at.is_(None)). \
        order_by(Dir.name). \
        limit(limit).offset(limit * page). \
        all()
    temp = []
    for dirname in dirs:
        temp.append({
            'id': dirname.id,
            'name': dirname.name
        })

    return temp


def post_dir(name: str, user_id: int):
    dirname = Dir(
        name=name,
        user_id=user_id
    )
    db.session.add(dirname)
    session_commit()
    return dirname.id
