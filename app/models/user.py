import datetime
from app.models import db, session_commit
from app.models.model import User


def check_user(username: str):
    res = User.query.filter(User.username == username). \
        filter(User.delete_at.is_(None)).first()
    if res is not None:
        raise RuntimeError('user exist')


def add_user(username: str, password: str, parent: int, role: int):
    user = User(
        username=username,
        password=password,
        nickname=username,
        role=role,
        parent_id=parent,
    )

    db.session.add(user)
    session_commit()


def delete_user(temp_id: int, user_id: int):
    user = User.query.filter(User.id.in_(temp_id)).all()
    for item in user:
        if item.parent_id != user_id:
            raise RuntimeError('no auth')

    for item in user:
        item.delete_at = datetime.datetime.now()
    session_commit()


def get_user(user_id: int, username) -> (list, int):
    if username is None:
        sql = User.query. \
            filter(User.parent_id == user_id). \
            filter(User.delete_at.is_(None))
    else:
        sql = User.query. \
            filter(User.parent_id == user_id). \
            filter(User.delete_at.is_(None)). \
            filter(User.username.like('%{}%'.format(username)))
    temp = sql.all()
    count = sql.count()

    user = []
    for item in temp:
        user.append({
            'username': item.username,
            'nickname': item.nickname,
            'create_at': item.create_at.strftime('%Y-%m-%d %H:%M:%S'),
            'sex': item.sex
        })

    return user, count


def get_user_detail(user_id, this_user):
    user = User.query. \
        filter(User.id == this_user). \
        filter(User.parent_id == user_id). \
        filter(User.delete_at.is_(None)). \
        first()
    if user is None:
        raise RuntimeError('没有此用户')

    return {
        'username': user.username,
        'nickname': user.nickname,
        'sex': user.sex,
        'email': user.email,
        'phone': user.phone,
        'avatar': user.avatar,
        'create_at': user.create_at.strftime('%Y-%m-%d %H:%M:%S')
    }
