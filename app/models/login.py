from app.models.model import User


def confirm_user(username, password):
    temp_username = User.query. \
        filter_by(username=username). \
        filter_by(password=password). \
        filter_by(delete_at=None). \
        first()
    temp_phone = User.query. \
        filter_by(phone=username). \
        filter_by(password=password). \
        filter_by(delete_at=None). \
        first()
    if temp_username is not None:
        return temp_username
    elif temp_phone is not None:
        return temp_phone
    else:
        return None
