from flask import Flask
from app.controllers.login import login_page


def register_router(app: Flask):
    app.register_blueprint(login_page)
