from flask import Blueprint
from app.utils.warp import success_warp, fail_warp

notice_page = Blueprint('notice', __name__, url_prefix='/notice')


# class Notice(MethodView):
#     @staticmethod
#     def get(notice_id: int):
#         if notice_id is None:
#
#             return
#         else:
#             return
#
#
# notice_view = Notice.as_view('notice_api')
# notice_page.add_url_rule('', defaults={'notice_id': None}, view_func=notice_view, methods=['GET'])
# notice_page.add_url_rule('/<int:notice_id>', view_func=notice_view, methods=['GET', 'PUT'])
