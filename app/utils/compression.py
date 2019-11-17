import cv2


def compress(path: str) -> str:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    new_path = path.rsplit('.', 1)[0] + '.jpg'
    cv2.imwrite(new_path, img, [cv2.IMWRITE_JPEG_QUALITY, 30])

    return new_path
