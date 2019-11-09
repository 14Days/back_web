from flask import Flask
from app.config import set_config


def create_new_app() -> Flask:
    app = Flask(__name__)

    # 加载配置文件
    set_config(app)

    return app
