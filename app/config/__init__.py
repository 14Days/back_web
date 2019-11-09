import os
import pathlib
import yaml
from flask import Flask


def set_config(app: Flask):
    mode = os.environ.get('mode') if os.environ.get('mode') is not None else 'dev'
    path = pathlib.Path(__file__).parent.parent.parent
    path = pathlib.Path.joinpath(path, '{}.yaml'.format(mode))

    with open(str(path), 'rb') as f:
        config = yaml.safe_load(f.read())
        app.config.update(config)
