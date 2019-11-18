from flask import Blueprint, request, session
from app.utils.auth import auth_require, Permission

recommend_page = Blueprint('recommend', __name__, url_prefix='/img')


@recommend_page.route('', methods=['GET'])
@auth_require(Permission.ROOT | Permission.ADMIN | Permission.DESIGNER)
def recommend_get():
    pass
