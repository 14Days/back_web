import datetime
from app.models import session_commit
from app.models.model import Notice, User

"""
定义通知获取（抽象工厂）
"""


# 获取通知
class IGetNotice:
    _sql = None

    def get_result(self, user_id, limit, page, start_time, end_time, notice_type) -> (int, list):
        pass

    def _get_sql(self, limit, page, start_time, end_time, notice_type) -> (int, list):
        if start_time is not None:
            start = datetime.datetime.strptime(start_time, '%Y-%m-%d')
            self._sql = self._sql.filter(Notice.create_at >= start)
        if end_time is not None:
            end = datetime.datetime.strptime(end_time, '%Y-%m-%d')
            self._sql = self._sql.filter(Notice.create_at <= end)
        if notice_type is not None:
            self._sql = self._sql.filter(Notice.type == notice_type)

        count = self._sql.count()
        data = self._sql.order_by(Notice.is_top.desc()).limit(limit).offset(page * limit).all()

        res = []
        for item in data:
            res.append({
                'title': item.title,
                'create_at': item.create_at.strftime('%Y-%m-%d'),
                'user': item.user.nickname
            })

        return count, res


# root用户获取通知
class GetNoticeRoot(IGetNotice):
    def get_result(self, user_id, limit, page, start_time, end_time, notice_type) -> (int, list):
        self._sql = Notice.query
        return self._get_sql(limit, page, start_time, end_time, notice_type)


# 管理员获取通知
class GetNoticeAdmin(IGetNotice):
    def get_result(self, user_id, limit, page, start_time, end_time, notice_type) -> (int, list):
        self._sql = Notice.query.filter(Notice.user_id == user_id)
        return self._get_sql(limit, page, start_time, end_time, notice_type)


# 设计师获取通知
class GetNoticeDesigner(IGetNotice):
    def get_result(self, user_id, limit, page, start_time, end_time, notice_type) -> (int, list):
        parent = User.query.filter(User.id == user_id).first().parent_id
        self._sql = Notice.query.filter(Notice.user_id == parent)
        return self._get_sql(limit, page, start_time, end_time, notice_type)


# 工厂函数
class GetNotice:
    def __init__(self, role):
        if role == 1:
            self._get_res = GetNoticeRoot()
        elif role == 2:
            self._get_res = GetNoticeAdmin()
        elif role == 3:
            self._get_res = GetNoticeDesigner()
        else:
            raise RuntimeError('user error')

    def get_res(self, user_id, limit, page, start_time, end_time, notice_type):
        return self._get_res.get_result(user_id, limit, page, start_time, end_time, notice_type)
