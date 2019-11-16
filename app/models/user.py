import datetime
from app.models import db, session_commit
from app.models.model import User, Avatar


def check_user(username: str):
    """
    检测用户是否存在
    :param username:
    :return:
    """
    res = User.query.filter(User.username == username). \
        filter(User.delete_at.is_(None)).first()
    if res is not None:
        raise RuntimeError('user exist')


def add_user(username: str, password: str, parent: int, role: int):
    """
    新建用户
    :param username:
    :param password:
    :param parent:
    :param role: 用户角色
    :return:
    """
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
    """
    删除用户
    :param temp_id:
    :param user_id:
    :return:
    """
    user = User.query.filter(User.id.in_(temp_id)).all()
    for item in user:
        if item.parent_id != user_id:
            raise RuntimeError('no auth')

    for item in user:
        item.delete_at = datetime.datetime.now()
    session_commit()


def get_user(user_id: int, username) -> (list, int):
    """
    获得所有用户的信息，支持模糊查询
    :param user_id:
    :param username:
    :return:
    """
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
    """
    获取某一用户的详细信息
    :param user_id:
    :param this_user:
    :return:
    """
    user = User.query. \
        filter(User.id == this_user). \
        filter(User.parent_id == user_id). \
        filter(User.delete_at.is_(None)). \
        first()

    if user is None:
        raise RuntimeError('没有此用户')

    avatar = None
    if len(user.avatar) == 0:
        avatar = Avatar.query.filter_by(status=-1).first()
        user.avatar.append(avatar)
    else:
        for item in user.avatar:
            if item.status == 1:
                avatar = item
                break

    return {
        'username': user.username,
        'nickname': user.nickname,
        'sex': user.sex,
        'email': user.email,
        'phone': user.phone,
        'avatar': {
            'id': avatar.id,
            'name': avatar.name
        },
        'create_at': user.create_at.strftime('%Y-%m-%d %H:%M:%S')
    }


def save_avatar(name):
    """
    保存用户头像名称
    :param name:
    :return:
    """
    avatar = Avatar(name=name, status=0)
    db.session.add(avatar)
    session_commit()
    return avatar


def change_user_info(user_id, this_user, nickname, sex, email, phone, avatar):
    """
    修改个人信息
    :param user_id: 登陆用户
    :param this_user: 要修改的用户
    :param nickname:
    :param sex:
    :param email:
    :param phone:
    :param avatar:
    :return:
    """
    user = User.query.filter_by(id=this_user).first()

    if user.id != user_id and user.parent_id != user_id:
        raise RuntimeError('no auth')
    if avatar['old_id'] != avatar['new_id']:
        old_avatar = Avatar.query.filter_by(id=avatar['old_id']).first()
        if old_avatar.user_id != this_user:
            raise RuntimeError('no auth')

        new_avatar = Avatar.query.filter_by(id=avatar['new_id']).first()
        if new_avatar.status != 0:
            raise RuntimeError('no auth')

        old_avatar.status = 2
        new_avatar.status, new_avatar.user_id = 1, this_user

    user.nickname, user.sex, user.email, user.phone = nickname, sex, email, phone

    session_commit()
