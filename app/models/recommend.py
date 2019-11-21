import datetime
from app.models import db, session_commit
from app.models.model import Img, Recommend, User
from app.utils.errors import errors


def save_img(name):
    """
    保存用户上传图片
    :param name:
    :return:
    """
    img = Img(
        name=name,
        type=2,
    )
    db.session.add(img)
    session_commit()
    return img


# 定义推荐消息工厂
class IRecommend:
    _sql_all = None
    _sql_detail = None

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        pass

    def post_recommend(self, content: str, img: list, user_id: int):
        pass

    def delete_recommend(self):
        pass

    def put_recommend(self):
        pass

    def _get_recommend(self, limit, page, start_time, end_time, nickname, content):
        if start_time is not None:
            start = datetime.datetime.strptime(start_time, '%Y-%m-%d')
            self._sql_all = self._sql_all.filter(Recommend.create_at >= start)
        if end_time is not None:
            end = datetime.datetime.strptime(end_time, '%Y-%m-%d')
            self._sql_all = self._sql_all.filter(Recommend.create_at <= end)
        if nickname is not None:
            users = User.query.filter(User.nickname.like('%{}%'.format(nickname))).all()
            id_list = []
            for user in users:
                id_list.append(user.id)
            self._sql_all = self._sql_all.filter(Recommend.user_id.in_(id_list))
        if content is not None:
            self._sql_all = self._sql_all.filter(Recommend.content.like('%{}%'.format(content)))
        self._sql_all = self._sql_all.filter(Recommend.delete_at.is_(None))

        count = self._sql_all.count()
        data = self._sql_all.order_by(Recommend.create_at.desc()).limit(limit).offset(page * limit).all()

        res = []
        for item in data:
            temp = {
                'id': item.id,
                'content': item.content,
                'thumb': len(item.thumbs),
                'comment': len(item.comment)
            }
            temp_img = []
            for img_item in item.img:
                if img_item.delete_at is None:
                    temp_img.append({
                        'id': img_item.id,
                        'name': img_item.name
                    })
            temp['img_url'] = temp_img
            res.append(temp)

        return count, res

    @staticmethod
    def _post_recommend(content: str, img: list, user_id: int):
        """
        发布推荐消息推荐类
        :param content:
        :param img:
        :return:
        """
        image = Img.query.filter(Img.id.in_(img)).first()
        recommend = Recommend(content=content)
        recommend.img.append(image)
        user = User.query.filter_by(id=user_id).first()
        user.recommend.append(recommend)

        session_commit()


class RecommendRoot(IRecommend):
    """
    Root用户控制类
    """

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        self._sql_all = Recommend.query
        return self._get_recommend(limit, page, start_time, end_time, nickname, content)

    def post_recommend(self, content: str, img: list, user_id: int):
        self._post_recommend(content, img, user_id)


class RecommendAdmin(IRecommend):
    """
    Admin用户控制类
    """

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        users = User.query.filter(User.parent_id == user_id).all()
        id_list = [user_id]
        for user in users:
            id_list.append(user.id)
        self._sql_all = Recommend.query.filter(Recommend.id.in_(id_list))
        return self._get_recommend(limit, page, start_time, end_time, nickname, content)

    def post_recommend(self, content: str, img: list, user_id: int):
        self._post_recommend(content, img, user_id)


class RecommendDesigner(IRecommend):
    """
    设计师控制类
    """

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        self._sql_all = Recommend.query.filter(Recommend.user_id == user_id)
        return self._get_recommend(limit, page, start_time, end_time, nickname, content)

    def post_recommend(self, content: str, img: list, user_id: int):
        self._post_recommend(content, img, user_id)


class GetRecommend:
    def __init__(self, role):
        if role == 1:
            self._get_res = RecommendRoot()
        elif role == 2:
            self._get_res = RecommendAdmin()
        elif role == 3:
            self._get_res = RecommendDesigner()
        else:
            raise RuntimeError(errors['402'])

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        return self._get_res.get_recommend(limit, page, start_time, end_time, nickname, content, user_id)

    def post_recommend(self, content, img, user_id):
        self._get_res.post_recommend(content, img, user_id)
