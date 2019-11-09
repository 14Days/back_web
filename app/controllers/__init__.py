from flask import Flask
from app.middlewares.auth import auth_mid
from app.controllers.login import login_page
from app.controllers.user import user_page


def register_router(app: Flask):
    app.register_blueprint(login_page)
    auth_mid(user_page)
    app.register_blueprint(user_page)
