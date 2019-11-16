import pytest


class TestLogin:
    @pytest.mark.parametrize(
        ('username', 'password'),
        (('root', '123456'), ('gyk', '123456'))
    )
    def test_post(self, client, username, password):
        rv = client.post('/login', json={
            'username': username,
            'password': password
        })

        assert rv.status_code == 200
        data = rv.get_json()
        print(data)
        assert data['status'] == 'success'
