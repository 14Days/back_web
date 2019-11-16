import pytest
from main import app as real_app


@pytest.fixture
def app():
    return real_app


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='root', password='123456'):
        return self._client.post('/login', json={
            'username': username,
            'password': password
        })

    def logout(self):
        return self._client.delete('/login')


@pytest.fixture
def auth_client(client):
    return AuthActions(client)
