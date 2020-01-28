FROM python:3.7-alpine AS base
WORKDIR /app

FROM base AS dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple \
    && /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' >/etc/timezone

FROM dependencies AS release
ADD . /app
CMD ["gunicorn", "main:app", "-c", "gunicorn.conf.py"]