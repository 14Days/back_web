import os
import pathlib
from PIL import Image
from app.utils.md5 import file_md5


def compress(path: str):
    img = Image.open(path)
    img.save(path)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def deal_img(dirname, f):
    _UPLOAD_FOLDER = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent.parent, dirname)

    file_path = pathlib.Path.joinpath(_UPLOAD_FOLDER, f.filename)
    f.save(str(file_path))
    # 压缩图片
    compress(str(file_path))

    # 文件重命名
    name = file_md5(str(file_path)) + '.jpg'
    os.rename(
        str(file_path),
        str(pathlib.Path.joinpath(_UPLOAD_FOLDER, name))
    )

    return name
