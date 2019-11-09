import datetime
from app.models import db


class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, nullable=True)
    sex = db.Column(db.Integer, nullable=True, default=1)
    email = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    avatar = db.Column(db.String, nullable=False, default='avatar')
    # 1：root、2：管理员、3：设计师
    role = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
