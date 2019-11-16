import pytest


class TestUser:
    @pytest.mark.parametrize(
        ('username', 'password'),
        (('root', '123456'), ('gyk', '123456'))
    )
    def test_get_all(self, client, auth_client, username, password):
        auth_client.login(username, password)
        with client:
            rv = client.get('/user')
            assert rv.status_code == 200
            data = rv.get_json()
            assert data['status'] == 'success'
