from app.models import db
from app.models.model import AppUser, Recommend, thumb, favorite


class RecordBuild:
    def __init__(self, start, end):
        self.start = start
        self.end = end

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
                    like[tag.name] = 0

        like_temp = []
        for item in like.keys():
            like_temp.append({
                'tag': item,
                'num': like[item]
            })
        return like_temp

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

    def get_res(self):
        return {
            'register': self._get_register(),
            'recommend': self._get_recommend(),
            'style': self._get_style()
        }
