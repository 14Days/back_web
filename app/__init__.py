from flask import Flask
from app.config import set_config
from app.utils.logger import create_log
from app.controllers import register_router
from app.models import connect_db


def create_new_app() -> Flask:
    app = Flask(__name__)

    # 加载配置文件
    set_config(app)

    # 初始化log
    create_log(app)

    # 注册路由
    register_router(app)

    # 链接数据库
    connect_db(app)

    return app
