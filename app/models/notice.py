import datetime
from sqlalchemy import or_
from app.models import db, session_commit
from app.models.model import Notice, User
from app.utils.errors import errors

"""
定义通知获取（抽象工厂）
"""


# 获取通知
class INotice:
    _sql_all = None
    _sql_detail = None

    def get_all_result(self, user_id, limit, page, start_time, end_time, notice_type) -> (int, list):
        pass

    def get_detail(self, user_id, notice_id):
        pass

    def post_notice(self, title, content, is_top, notice_type, user_id):
        pass

    def _get_all_sql(self, limit, page, start_time, end_time, notice_type) -> (int, list):
        if start_time is not None:
            start = datetime.datetime.strptime(start_time, '%Y-%m-%d')
            self._sql_all = self._sql_all.filter(Notice.create_at >= start)
        if end_time is not None:
            end = datetime.datetime.strptime(end_time, '%Y-%m-%d')
            self._sql_all = self._sql_all.filter(Notice.create_at <= end)
        if notice_type is not None:
            self._sql_all = self._sql_all.filter(Notice.type == notice_type)
        self._sql_all = self._sql_all.filter(Notice.delete_at.is_(None))

        count = self._sql_all.count()
        data = self._sql_all.order_by(Notice.is_top.desc()).limit(limit).offset(page * limit).all()

        res = []
        for item in data:
            res.append({
                'id': item.id,
                'title': item.title,
                'create_at': item.create_at.strftime('%Y-%m-%d'),
                'user': item.user.nickname
            })

        return count, res

    def _get_detail_sql(self, notice_id):
        temp = self._sql_detail.filter(Notice.id == notice_id).filter(Notice.delete_at.is_(None)).first()

        if temp is None:
            raise RuntimeError(errors['501'])

        return {
            'id': temp.id,
            'title': temp.title,
            'content': temp.content,
            'create_at': temp.create_at.strftime('%Y-%m-%d'),
            'user': temp.user.nickname,
            'is_top': temp.is_top,
            'type': temp.type
        }

    @staticmethod
    def _post_notice(title, content, is_top, notice_type, user_id):
        notice = Notice(
            title=title,
            content=content,
            is_top=is_top,
            type=notice_type,
            user_id=user_id
        )

        db.session.add(notice)
        session_commit()


# root用户获取通知
class NoticeRoot(INotice):
    def get_all_result(self, user_id, limit, page, start_time, end_time, notice_type) -> (int, list):
        self._sql_all = Notice.query
        return self._get_all_sql(limit, page, start_time, end_time, notice_type)

    def get_detail(self, user_id, notice_id):
        self._sql_detail = Notice.query
        return self._get_detail_sql(notice_id)

    def post_notice(self, title, content, is_top, notice_type, user_id):
        self._post_notice(title, content, is_top, notice_type, user_id)


# 管理员获取通知
class NoticeAdmin(INotice):
    def get_all_result(self, user_id, limit, page, start_time, end_time, notice_type) -> (int, list):
        self._sql_all = Notice.query.filter(or_(Notice.user_id == user_id, Notice.type == 1))
        return self._get_all_sql(limit, page, start_time, end_time, notice_type)

    def get_detail(self, user_id, notice_id):
        self._sql_detail = Notice.query.filter(or_(Notice.user_id == user_id, Notice.type == 1))
        return self._get_detail_sql(notice_id)

    def post_notice(self, title, content, is_top, notice_type, user_id):
        if notice_type == 1:
            raise RuntimeError(errors['403'])
        self._post_notice(title, content, is_top, notice_type, user_id)


# 设计师获取通知
class NoticeDesigner(INotice):
    @staticmethod
    def _initial(user_id):
        root = User.query.filter(User.role == 1).first().parent_id
        parent = User.query.filter(User.id == user_id).first().parent_id

        return root, parent

    def get_all_result(self, user_id, limit, page, start_time, end_time, notice_type) -> (int, list):
        root, parent = self._initial(user_id)
        self._sql_all = Notice.query. \
            filter(or_(Notice.user_id == parent, Notice.user_id == root)). \
            filter(Notice.type == 2)

        return self._get_all_sql(limit, page, start_time, end_time, notice_type)

    def get_detail(self, user_id, notice_id):
        root, parent = self._initial(user_id)
        self._sql_detail = Notice.query. \
            filter(or_(Notice.user_id == parent, Notice.user_id == root)). \
            filter(Notice.type == 2)
        return self._get_detail_sql(notice_id)


# 工厂函数
class GetNotice:
    def __init__(self, role):
        if role == 1:
            self._get_res = NoticeRoot()
        elif role == 2:
            self._get_res = NoticeAdmin()
        elif role == 3:
            self._get_res = NoticeDesigner()
        else:
            raise RuntimeError(errors['402'])

    def get_all_res(self, user_id, limit, page, start_time, end_time, notice_type):
        return self._get_res.get_all_result(user_id, limit, page, start_time, end_time, notice_type)

    def get_detail_res(self, user_id, notice_id):
        return self._get_res.get_detail(user_id, notice_id)

    def post_notice(self, title, content, is_top, notice_type, user_id):
        self._get_res.post_notice(title, content, is_top, notice_type, user_id)
