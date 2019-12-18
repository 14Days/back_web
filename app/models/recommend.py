import datetime
from app.models import db, session_commit
from app.models.model import Img, Recommend, User, AppAvatar
from app.utils.errors import errors


def save_img(name, user_id):
    """
    保存用户上传图片
    :param name:
    :param user_id
    :return:
    """
    img = Img(
        name=name,
        user_id=user_id
    )
    db.session.add(img)
    session_commit()
    return img


# 定义推荐消息工厂
class IRecommend:
    _sql_all = None
    _sql_detail = None
    _sql_put = None

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        pass

    def get_recommend_detail(self, user_id, recommend_id):
        pass

    def post_recommend(self, content: str, img: list, user_id: int):
        pass

    def delete_recommend(self, user_id, recommend_ids: list):
        pass

    def put_recommend(self, content, new_img_id: list, old_img_id: list, user_id: int, recommend_id: int):
        pass

    def _get_recommend(self, limit, page, start_time, end_time, nickname, content):
        """
        得到所有通知接口
        :param limit:
        :param page:
        :param start_time:
        :param end_time:
        :param nickname:
        :param content:
        :return:
        """
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
                temp_img.append({
                    'id': img_item.id,
                    'name': img_item.name
                })
            temp['img_url'] = temp_img
            res.append(temp)

        return count, res

    def _get_recommend_detail(self, recommend_id):
        """
        获得推荐消息详情
        :param recommend_id:
        :return:
        """
        res: Recommend = self._sql_detail.filter(Recommend.id == recommend_id). \
            filter(Recommend.delete_at.is_(None)).first()
        # 是否存在
        if res is None:
            raise RuntimeError(errors['501'])

        # 得到点赞用户
        thumb_user = []
        for user in res.thumbs:
            thumb_user.append(user.nickname)

        # 得到评论
        comment = []
        for top in res.comment:
            # 一级评论
            if top.delete_at is None:
                # 用户头像
                top_avatar = AppAvatar.query.filter(AppAvatar.status == -1).first()
                top_avatars = top.app_user.avatar
                for item in top_avatars:
                    if item.status == 1:
                        top_avatar = item
                temp_comment = {
                    'id': top.id,
                    'content': top.content,
                    'create_at': top.create_at.strftime('%Y-%m-%d'),
                    'user': {
                        'id': top.app_user.id,
                        'nickname': top.app_user.nickname,
                        'avatar': top_avatar.name
                    }
                }
                temp_second = []
                for second in top.second_comment:
                    if second.delete_at is None:
                        second_avatar = AppAvatar.query.filter(AppAvatar.status == -1).first()
                        second_avatars = second.app_user.avatar
                        for item in second_avatars:
                            if item.status == 1:
                                second_avatar = item
                        temp_second.append({
                            'id': second.id,
                            'content': second.content,
                            'create_at': second.create_at.strftime('%Y-%m-%d'),
                            'user': {
                                'id': second.app_user.id,
                                'nickname': second.app_user.nickname,
                                'avatar': second_avatar.name
                            }
                        })
                temp_comment['second'] = temp_second
                comment.append(temp_comment)
        # 得到图片url
        temp_img = []
        for img_item in res.img:
            temp_img.append({
                'id': img_item.id,
                'name': img_item.name
            })

        recommend_avatar = AppAvatar.query.filter(AppAvatar.status == -1).first()
        recommend_avatars = res.user.avatar
        for item in recommend_avatars:
            if item.status == 1:
                recommend_avatar = item

        return {
            'id': res.id,
            'content': res.content,
            'img': temp_img,
            'user': {
                'id': res.user.id,
                'nickname': res.user.nickname,
                'avatar': recommend_avatar.name
            },
            'thumb_user': thumb_user,
            'create_at': res.create_at.strftime('%Y-%m-%d'),
            'comment': comment
        }

    @staticmethod
    def _post_recommend(content: str, img: list, user_id: int):
        """
        发布推荐消息推荐类
        :param content:
        :param img:
        :return:
        """
        # 图片使用数加一
        image = Img.query.filter(Img.id.in_(img)).all()
        for item in image:
            item.type = item.type + 1
        recommend = Recommend(content=content)
        recommend.img.extend(image)
        user = User.query.filter_by(id=user_id).first()
        user.recommend.append(recommend)

        session_commit()

        return recommend.id

    def _put_recommend(self, content, new_img_id: list, old_img_id: list, recommend_id: int):
        recommend = self._sql_put.filter(Recommend.id == recommend_id). \
            filter(Recommend.delete_at.is_(None)). \
            first()
        if recommend is None:
            raise RuntimeError(errors['501'])

        recommend.content = content
        old = Img.query.filter(Img.id.in_(old_img_id)).all()
        for item in old:
            item.type = item.type - 1
            recommend.img.remove(item)
        new = Img.query.filter(Img.id.in_(new_img_id)).all()
        for item in new:
            item.type = item.type + 1
        recommend.img = new
        session_commit()

        return recommend.id

    @staticmethod
    def _delete_recommend(recommends):
        if recommends is None:
            raise RuntimeError(errors['501'])
        for item in recommends:
            for img in item.img:
                img.type = img.type - 1
            item.delete_at = datetime.datetime.now()


class RecommendRoot(IRecommend):
    """
    Root用户控制类
    """

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        self._sql_all = Recommend.query
        return self._get_recommend(limit, page, start_time, end_time, nickname, content)

    def get_recommend_detail(self, user_id, recommend_id):
        self._sql_detail = Recommend.query
        return self._get_recommend_detail(recommend_id)

    def post_recommend(self, content: str, img: list, user_id: int):
        return self._post_recommend(content, img, user_id)

    def put_recommend(self, content, new_img_id: list, old_img_id: list, user_id: int, recommend_id: int):
        self._sql_put = Recommend.query
        return self._put_recommend(content, new_img_id, old_img_id, recommend_id)

    def delete_recommend(self, user_id, recommend_ids: list):
        recommends = Recommend.query.filter(Recommend.id.in_(recommend_ids)).all()
        self._delete_recommend(recommends)
        session_commit()


class RecommendAdmin(IRecommend):
    """
    Admin用户控制类
    """

    @staticmethod
    def _get_user_list(user_id):
        users = User.query.filter(User.parent_id == user_id).all()
        id_list = [user_id]
        for user in users:
            id_list.append(user.id)
        return id_list

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        id_list = self._get_user_list(user_id)
        self._sql_all = Recommend.query.filter(Recommend.user_id.in_(id_list))
        return self._get_recommend(limit, page, start_time, end_time, nickname, content)

    def get_recommend_detail(self, user_id, recommend_id):
        id_list = self._get_user_list(user_id)
        self._sql_detail = Recommend.query.filter(Recommend.id.in_(id_list))
        return self._get_recommend_detail(recommend_id)

    def post_recommend(self, content: str, img: list, user_id: int):
        return self._post_recommend(content, img, user_id)

    def put_recommend(self, content, new_img_id: list, old_img_id: list, user_id: int, recommend_id: int):
        id_list = self._get_user_list(user_id)
        self._sql_put = Recommend.query.filter(Recommend.id.in_(id_list))
        return self._put_recommend(content, new_img_id, old_img_id, recommend_id)

    def delete_recommend(self, user_id, recommend_ids: list):
        id_list = self._get_user_list(user_id)
        recommends = Recommend.query. \
            filter(Recommend.id.in_(recommend_ids)). \
            filter(Recommend.user_id.in_(id_list)). \
            all()
        self._delete_recommend(recommends)
        session_commit()


class RecommendDesigner(IRecommend):
    """
    设计师控制类
    """

    def get_recommend(self, limit, page, start_time, end_time, nickname, content, user_id):
        self._sql_all = Recommend.query.filter(Recommend.user_id == user_id)
        return self._get_recommend(limit, page, start_time, end_time, nickname, content)

    def get_recommend_detail(self, user_id, recommend_id):
        self._sql_detail = Recommend.query.filter(Recommend.user_id == user_id)
        return self._get_recommend_detail(recommend_id)

    def post_recommend(self, content: str, img: list, user_id: int):
        return self._post_recommend(content, img, user_id)

    def put_recommend(self, content, new_img_id: list, old_img_id: list, user_id: int, recommend_id: int):
        self._sql_put = Recommend.query.filter(Recommend.user_id == user_id)
        return self._put_recommend(content, new_img_id, old_img_id, recommend_id)

    def delete_recommend(self, user_id, recommend_ids: list):
        recommends = Recommend.query. \
            filter(Recommend.id.in_(recommend_ids)). \
            filter(Recommend.user_id == user_id). \
            all()
        self._delete_recommend(recommends)
        session_commit()


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

    def get_recommend_detail(self, user_id, recommend_id):
        return self._get_res.get_recommend_detail(user_id, recommend_id)

    def post_recommend(self, content, img, user_id):
        return self._get_res.post_recommend(content, img, user_id)

    def put_recommend(self, content, new_img_id: list, old_img_id: list, user_id: int, recommend_id: int):
        return self._get_res.put_recommend(content, new_img_id, old_img_id, user_id, recommend_id)

    def delete_recommend(self, user_id, recommend_id):
        self._get_res.delete_recommend(user_id, recommend_id)
