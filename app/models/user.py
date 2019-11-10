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
