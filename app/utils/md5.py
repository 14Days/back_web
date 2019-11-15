import hashlib


def encode_md5(temp: str) -> str:
    md5 = hashlib.md5()
    md5.update(temp.encode(encoding='utf-8'))

    return md5.hexdigest()


def file_md5(file_path) -> str:
    with open(file_path, 'rb') as f:
        md5_obj = hashlib.md5()
        while True:
            d = f.read(8096)
            if not d:
                break
            md5_obj.update(d)
        hash_code = md5_obj.hexdigest()
        return str(hash_code).lower()
