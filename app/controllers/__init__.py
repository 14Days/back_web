from flask import Flask
from app.middlewares.auth import auth_mid
from app.controllers.login import login_page
from app.controllers.user import user_page
from app.controllers.notice import notice_page
from app.controllers.recommend import recommend_page


def register_router(app: Flask):
    # 登陆退出
    app.register_blueprint(login_page)

    # 用户路由
    auth_mid(user_page)
    app.register_blueprint(user_page)

    # 通知路由
    auth_mid(notice_page)
    app.register_blueprint(notice_page)

    # 推荐消息路由
    auth_mid(recommend_page)
    app.register_blueprint(recommend_page)
