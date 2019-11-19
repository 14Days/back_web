from app.models import db, session_commit
from app.models.model import Img


def save_img(name):
    img = Img(
        name=name,
        type=2,
    )
    db.session.add(img)
    session_commit()
    return img
