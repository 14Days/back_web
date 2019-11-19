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

    def get_all_result(self, user_id, limit, page, start_time, end_time, notice_type, title) -> (int, list):
        """
        得到用户权限下的所有结果
        :param title:
        :param user_id:
        :param limit:
        :param page:
        :param start_time:
        :param end_time:
        :param notice_type:
        :return:
        """
        pass

    def get_detail(self, user_id, notice_id):
        """
        得到用户权限下的通知详情
        :param user_id:
        :param notice_id:
        :return:
        """
        pass

    def post_notice(self, title, content, is_top, notice_type, user_id):
        """
        用户发布通知
        :param title:
        :param content:
        :param is_top:
        :param notice_type:
        :param user_id:
        :return:
        """
        pass

    def delete_notice(self, user_id: int, notice_id: list):
        pass

    def put_notice(self, title, content, is_top, notice_type, user_id, notice_id):
        pass

    def _get_all_sql(self, limit, page, start_time, end_time, notice_type, title) -> (int, list):
        """
        用户获取通知的基本处理函数，主要处理搜索条件
        :param limit:
        :param page:
        :param start_time:
        :param end_time:
        :param notice_type:
        :return:
        """
        if start_time is not None:
            start = datetime.datetime.strptime(start_time, '%Y-%m-%d')
            self._sql_all = self._sql_all.filter(Notice.create_at >= start)
        if end_time is not None:
            end = datetime.datetime.strptime(end_time, '%Y-%m-%d')
            self._sql_all = self._sql_all.filter(Notice.create_at <= end)
        if notice_type is not None:
            self._sql_all = self._sql_all.filter(Notice.type == notice_type)
        if title is not None:
            self._sql_all = self._sql_all.filter(Notice.title.like('%{}%'.format(title)))
        self._sql_all = self._sql_all.filter(Notice.delete_at.is_(None))

        count = self._sql_all.count()
        data = self._sql_all.order_by(Notice.is_top.desc()).limit(limit).offset(page * limit).all()

        res = []
        for item in data:
            res.append({
                'id': item.id,
                'title': item.title,
                'content': item.content,
                'create_at': item.create_at.strftime('%Y-%m-%d'),
                'user': item.user.nickname,
                'is_top': item.is_top,
                'user_type': item.user.role
            })

        return count, res

    def _get_detail_sql(self, notice_id):
        """
        用户得到详细通知的基本处理
        :param notice_id:
        :return:
        """
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
        """
        发布通知的基本函数
        :param title:
        :param content:
        :param is_top:
        :param notice_type:
        :param user_id:
        :return:
        """
        notice = Notice(
            title=title,
            content=content,
            is_top=is_top,
            type=notice_type,
            user_id=user_id
        )

        db.session.add(notice)
        session_commit()

    @staticmethod
    def _put_notice(title, content, is_top, notice_type, notice: Notice):
        notice.title = title
        notice.content = content
        notice.is_top = is_top
        notice.type = notice_type
        session_commit()


class NoticeRoot(INotice):
    """
    root用户控制类
    """

    def get_all_result(self, user_id, limit, page, start_time, end_time, notice_type, title) -> (int, list):
        self._sql_all = Notice.query
        return self._get_all_sql(limit, page, start_time, end_time, notice_type, title)

    def get_detail(self, user_id, notice_id):
        self._sql_detail = Notice.query
        return self._get_detail_sql(notice_id)

    def post_notice(self, title, content, is_top, notice_type, user_id):
        self._post_notice(title, content, is_top, notice_type, user_id)

    def delete_notice(self, user_id: int, notice_id: list):
        notice = Notice.query.filter(Notice.id.in_(notice_id)).all()
        for item in notice:
            item.delete_at = datetime.datetime.now()
        session_commit()

    def put_notice(self, title, content, is_top, notice_type, user_id, notice_id):
        notice = Notice.query.filter(Notice.id == notice_id).first()
        self._put_notice(title, content, is_top, notice_type, notice)


class NoticeAdmin(INotice):
    """
    管理员控制类
    """

    def get_all_result(self, user_id, limit, page, start_time, end_time, notice_type, title) -> (int, list):
        self._sql_all = Notice.query.filter(or_(Notice.user_id == user_id, Notice.type == 1))
        return self._get_all_sql(limit, page, start_time, end_time, notice_type, title)

    def get_detail(self, user_id, notice_id):
        self._sql_detail = Notice.query.filter(or_(Notice.user_id == user_id, Notice.type == 1))
        return self._get_detail_sql(notice_id)

    def post_notice(self, title, content, is_top, notice_type, user_id):
        if notice_type == 1:
            raise RuntimeError(errors['403'])
        self._post_notice(title, content, is_top, notice_type, user_id)

    def delete_notice(self, user_id: int, notice_id: list):
        notice = Notice.query.filter(Notice.id.in_(notice_id)).all()

        for item in notice:
            if item.user_id != user_id:
                raise RuntimeError(errors['403'])

        for item in notice:
            item.delete_at = datetime.datetime.now()
        session_commit()

    def put_notice(self, title, content, is_top, notice_type, user_id, notice_id):
        notice = Notice.query.filter(Notice.id == notice_id).filter(Notice.user_id == user_id).first()
        if notice is None:
            raise RuntimeError(errors['403'])

        self._put_notice(title, content, is_top, notice_type, notice)


class NoticeDesigner(INotice):
    """
    设计师的控制类
    """

    @staticmethod
    def _initial(user_id):
        root = User.query.filter(User.role == 1).first().parent_id
        parent = User.query.filter(User.id == user_id).first().parent_id

        return root, parent

    def get_all_result(self, user_id, limit, page, start_time, end_time, notice_type, title) -> (int, list):
        root, parent = self._initial(user_id)
        self._sql_all = Notice.query. \
            filter(or_(Notice.user_id == parent, Notice.user_id == root)). \
            filter(Notice.type == 2)

        return self._get_all_sql(limit, page, start_time, end_time, notice_type, title)

    def get_detail(self, user_id, notice_id):
        root, parent = self._initial(user_id)
        self._sql_detail = Notice.query. \
            filter(or_(Notice.user_id == parent, Notice.user_id == root)). \
            filter(Notice.type == 2)
        return self._get_detail_sql(notice_id)


class GetNotice:
    """
    工厂函数通过不同的用户角色实例化
    """

    def __init__(self, role):
        if role == 1:
            self._get_res = NoticeRoot()
        elif role == 2:
            self._get_res = NoticeAdmin()
        elif role == 3:
            self._get_res = NoticeDesigner()
        else:
            raise RuntimeError(errors['402'])

    def get_all_res(self, user_id, limit, page, start_time, end_time, notice_type, title):
        return self._get_res.get_all_result(user_id, limit, page, start_time, end_time, notice_type, title)

    def get_detail_res(self, user_id, notice_id):
        return self._get_res.get_detail(user_id, notice_id)

    def post_notice(self, title, content, is_top, notice_type, user_id):
        self._get_res.post_notice(title, content, is_top, notice_type, user_id)

    def delete_notice(self, user_id, notice_id):
        self._get_res.delete_notice(user_id, notice_id)

    def put_notice(self, title, content, is_top, notice_type, user_id, notice_id):
        self._get_res.put_notice(title, content, is_top, notice_type, user_id, notice_id)
