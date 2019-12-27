from app.models import db
from app.models.model import AppUser, Recommend, thumb, favorite, Img, app_user_user, User


class RecordBuild:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @staticmethod
    def _dict2array(res: dict, name):
        def num_sort(ele):
            return ele['num']

        temp = []
        for item in res.keys():
            temp.append({
                name: item,
                'num': res[item]
            })

        for _ in range(len(temp), 10):
            temp.append({
                name: '无',
                'num': 0
            })

        temp.sort(key=num_sort, reverse=True)

        return temp

    def _style_item(self, table):
        temp = db.session.query(table). \
            filter(table.c.create_at >= self.start). \
            filter(table.c.create_at <= self.end). \
            all()
        like = {}
        for item in temp:
            recommend = Recommend.query.filter(Recommend.id == item.recommend_id).first()
            for tag in recommend.tags:
                if tag.name in like:
                    like[tag.name] += 1
                else:
                    like[tag.name] = 1

        return self._dict2array(like, 'tag')

    def _get_register(self):
        return AppUser.query.filter(AppUser.create_at >= self.start). \
            filter(AppUser.create_at <= self.end).count()

    def _get_recommend(self):
        return Recommend.query.filter(Recommend.create_at >= self.start). \
            filter(Recommend.create_at <= self.end). \
            filter(Recommend.delete_at.is_(None)). \
            count()

    def _get_style(self):
        thumbs = self._style_item(thumb)
        collections = self._style_item(favorite)

        return {
            'like': thumbs,
            'collect': collections
        }

    def _get_designer(self):
        # 上传图片
        images = Img.query.filter(Img.create_at >= self.start). \
            filter(Img.create_at <= self.end). \
            filter(Img.delete_at.is_(None)). \
            all()

        temp_img = {}
        for item in images:
            if item.user.nickname in temp_img:
                temp_img[item.user.nickname] += 1
            else:
                temp_img[item.user.nickname] = 1

        # 获取关注信息
        follow = db.session.query(app_user_user). \
            filter(app_user_user.c.create_at >= self.start). \
            filter(app_user_user.c.create_at <= self.end). \
            all()

        temp_follow = {}
        for item in follow:
            user = User.query.filter(User.id == item.user_id).first()
            if user.nickname in temp_follow:
                temp_follow[user.nickname] += 1
            else:
                temp_follow[user.nickname] = 1

        # 获取点赞
        thumbs = db.session.query(thumb). \
            filter(thumb.c.create_at >= self.start). \
            filter(thumb.c.create_at <= self.end). \
            all()

        temp_thumb = {}
        for item in thumbs:
            recommend = Recommend.query.filter(Recommend.id == item.recommend_id).first()
            if recommend.user.nickname in temp_thumb:
                temp_thumb[recommend.user.nickname] += 1
            else:
                temp_thumb[recommend.user.nickname] = 1

        return {
            'post': self._dict2array(temp_img, 'name'),
            'follow': self._dict2array(temp_follow, 'name'),
            'like': self._dict2array(temp_thumb, 'name')
        }

    def get_res(self):
        return {
            'register': self._get_register(),
            'recommend': self._get_recommend(),
            'style': self._get_style(),
            'designer': self._get_designer()
        }
