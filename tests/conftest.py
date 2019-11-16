import pytest
from main import app as real_app


@pytest.fixture
def app():
    return real_app


@pytest.fixture
def client(app):
    return app.test_client()
