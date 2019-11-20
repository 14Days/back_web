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
    def get_recommend(self):
        pass

    def post_recommend(self, content: str, img: list, user_id: int):
        pass

    def delete_recommend(self):
        pass

    def put_recommend(self):
        pass

    @staticmethod
    def _post_recommend(content: str, img: list, user_id: int):
        """
        发布推荐消息推荐类
        :param content:
        :param img:
        :return:
        """
        user = User.query.filter_by(id=user_id)
        user.recommend.append(
            Recommend(
                content=content,
                # img=img
            )
        )

        db.session.add(user)
        session_commit()


class RecommendRoot(IRecommend):
    """
    Root用户控制类
    """

    def post_recommend(self, content: str, img: list, user_id: int):
        self._post_recommend(content, img, user_id)


class RecommendAdmin(IRecommend):
    """
    Admin用户控制类
    """

    def post_recommend(self, content: str, img: list, user_id: int):
        self._post_recommend(content, img, user_id)


class RecommendDesigner(IRecommend):
    """
    设计师控制类
    """

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

    def post_recommend(self, content, img, user_id):
        self._get_res.post_recommend(content, img, user_id)
