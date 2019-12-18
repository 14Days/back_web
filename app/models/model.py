import datetime
from app.models import db


class User(db.Model):
    """
    用户数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, nullable=True)
    sex = db.Column(db.Integer, nullable=True, default=1)
    email = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    # 1：root、2：管理员、3：设计师
    role = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    avatar = db.relationship('Avatar', backref='user', lazy=True)
    notice = db.relationship('Notice', backref='user', lazy=True)
    recommend = db.relationship('Recommend', backref='user', lazy=True)
    images = db.relationship('Img', backref='user', lazy=True)


class Avatar(db.Model):
    """
    用户头像数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    # -1默认头像 0未使用 1 正在使用 2 曾经使用
    status = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Notice(db.Model):
    """
    通知消息数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.Integer, nullable=False)
    is_top = db.Column(db.Integer, nullable=False, default=0)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


# 用户点赞关系
thumb = db.Table(
    'thumb',
    db.Column('app_user_id', db.Integer, db.ForeignKey('app_user.id'), primary_key=True),
    db.Column('recommend_id', db.Integer, db.ForeignKey('recommend.id'), primary_key=True),
    db.Column('create_at', db.DateTime, default=datetime.datetime.now)
)

favorite = db.Table(
    'favorite',
    db.Column('app_user_id', db.Integer, db.ForeignKey('app_user.id'), primary_key=True),
    db.Column('recommend_id', db.Integer, db.ForeignKey('recommend.id'), primary_key=True),
    db.Column('create_at', db.DateTime, default=datetime.datetime.now)
)

# 标签推荐信息关系
tag_recommend = db.Table(
    'tag_recommend',
    db.Column('tag_id', db.Integer, db.ForeignKey('second_tag.id'), primary_key=True),
    db.Column('recommend_id', db.Integer, db.ForeignKey('recommend.id'), primary_key=True)
)

# 推荐消息图片关系
recommend_img = db.Table(
    'recommend_img',
    db.Column('recommend_id', db.Integer, db.ForeignKey('recommend.id'), primary_key=True),
    db.Column('img_id', db.Integer, db.ForeignKey('img.id'), primary_key=True)
)


class AppUser(db.Model):
    """
    app用户数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, nullable=True)
    sex = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    avatar = db.relationship('AppAvatar', backref='app_user', lazy=True)
    top_comment = db.relationship('TopComment', backref='app_user', lazy=True)
    second_comment = db.relationship('SecondComment', backref='app_user', lazy=True)


class AppAvatar(db.Model):
    """
    app用户头像
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    # -1默认头像 0未使用 1 正在使用 2 曾经使用
    status = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=True)


class Recommend(db.Model):
    """
    推荐消息数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.String, nullable=True)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    img = db.relationship('Img', secondary=recommend_img, lazy='subquery')
    thumbs = db.relationship('AppUser', secondary=thumb, lazy='subquery')
    comment = db.relationship('TopComment', backref='recommend', lazy=True)
    tags = db.relationship('SecondTag', secondary=tag_recommend, lazy='subquery')


class Dir(db.Model):
    """
    图片分类
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    images = db.relationship('Img', backref='dir', lazy=True)


class Img(db.Model):
    """
    推荐消息图片模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.Integer, nullable=False, default=0)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    recommend_id = db.Column(db.Integer, db.ForeignKey('recommend.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    dir_id = db.Column(db.Integer, db.ForeignKey('dir.id'), nullable=True, default=0)


class TopTag(db.Model):
    """
    一级风格数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    second_tag = db.relationship('SecondTag', backref='top_tag', lazy=True)


class SecondTag(db.Model):
    """
    二级风格数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    top_tag_id = db.Column(db.Integer, db.ForeignKey('top_tag.id'), nullable=False)
    recommends = db.relationship(
        'Recommend',
        secondary=tag_recommend,
        lazy='subquery',
        backref=db.backref('second_tags', lazy=True)
    )


class TopComment(db.Model):
    """
    一级评论数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.String, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    app_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=True)
    recommend_id = db.Column(db.Integer, db.ForeignKey('recommend.id'), nullable=True)
    second_comment = db.relationship('SecondComment', backref='top_comment', lazy=True)


class SecondComment(db.Model):
    """
    二级评论数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.String, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    app_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=True)
    top_comment_id = db.Column(db.Integer, db.ForeignKey('top_comment.id'), nullable=True)
