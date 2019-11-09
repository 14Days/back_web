from app.models import db, session_commit
from app.models.model import User


def check_user(username: str):
    res = User.query.filter_by(username=username).first()
    if res is not None:
        raise RuntimeError('user exist')


def add_user(username: str, password: str, parent: int, type: int):
    user = User(
        username=username,
        password=password,
        nickname=username,
        role=type,
        parent_id=parent,
    )

    db.session.add(user)
    session_commit()
