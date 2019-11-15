from flask import Flask
from app.middlewares.auth import auth_mid
from app.controllers.login import Login, login_page
from app.controllers.user import User, user_page


def register_router(app: Flask):
    # 登陆退出
    app.register_blueprint(login_page)

    # 用户路由
    auth_mid(user_page, 2)
    app.register_blueprint(user_page)
