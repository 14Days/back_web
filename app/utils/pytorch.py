import pathlib
import requests
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.models.model import Recommend, SecondTag

executor = ThreadPoolExecutor(max_workers=5)


def get_label(name: str):
    """
    获取标签
    """
    path = pathlib.Path(__file__).parent.parent.parent
    path = pathlib.Path.joinpath(path, 'img', name)
    # 发送请求
    files = {
        'file': (name, open(str(path), 'rb'), 'image/jpeg')
    }
    r = requests.post('http://prediction.wghtstudio.cn/color', files=files)
    data = r.json()
    if data['status'] == 'success':
        return data['tag_id']
    else:
        raise RuntimeError('ML error')


def label_recommend(recommend_id: int):
    """
    异步标记任务
    """
    try:
        print(db.session.query(Recommend))
        print(Recommend.query.filter(Recommend.id == recommend_id))
        recommend = Recommend.query.filter(Recommend.id == recommend_id).first()
        print(recommend)
        images = recommend.img
        tag_id = []
        for item in images:
            print(item.name)
            try:
                tag_id.append(get_label(item.name))
            except FileNotFoundError:
                continue
        tags = SecondTag.query.filter(SecondTag.id.in_(tag_id)).all()
        print(tags)
        recommend.tags.clear()
        recommend.tags.extend(tags)
        session_commit()
        print('done')
    except SQLAlchemyError as e:
        print(e.args)
