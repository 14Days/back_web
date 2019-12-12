import datetime
from app.models import session_commit
from app.models.model import TopComment, SecondComment, Recommend
from app.utils.errors import errors


class ILevel:
    def delete_it(self, comment_id):
        pass


class LevelTop(ILevel):
    def delete_it(self, comment_id):
        comment = TopComment.query. \
            filter(TopComment.id == comment_id). \
            filter(TopComment.delete_at.is_(None)). \
            first()
        return comment, comment.recommend_id


class LevelSecond(ILevel):
    def delete_it(self, comment_id):
        comment = SecondComment.query. \
            filter(SecondComment.id == comment_id). \
            filter(SecondComment.delete_at.is_(None)). \
            first()
        return comment, comment.top_comment.recommend_id


class IComment:
    def __init__(self, level):
        if level == 1:
            self._level = LevelTop()
        elif level == 2:
            self._level = LevelSecond()
        else:
            raise RuntimeError(errors['402'])

    def delete_comment(self, comment_id, user_id):
        pass


class CommentRoot(IComment):
    def delete_comment(self, comment_id, user_id):
        comment, recommend_id = self._level.delete_it(comment_id)
        if comment is None:
            raise RuntimeError(errors['501'])
        comment.delete_at = datetime.datetime.now()
        session_commit()


class CommentAdmin(IComment):
    def delete_comment(self, comment_id, user_id):
        comment, recommend_id = self._level.delete_it(comment_id)
        if comment is None:
            raise RuntimeError(errors['501'])

        recommend = Recommend.query. \
            filter(Recommend.id == recommend_id). \
            first()

        user = recommend.user
        if user.id != user_id and user.parent_id != user:
            raise RuntimeError(errors['403'])

        comment.delete_at = datetime.datetime.now()
        session_commit()


class CommentFactory:
    def __init__(self, role, level):
        if role == 1:
            self._comment = CommentRoot(level)
        elif role == 2:
            self._comment = CommentAdmin(level)
        else:
            raise RuntimeError(errors['402'])

    def delete_item(self, comment_id, user_id):
        self._comment.delete_comment(comment_id, user_id)
