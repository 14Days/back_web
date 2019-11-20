import pytest


class TestRecommend:
    @pytest.mark.parametrize(
        ('username', 'password'),
        (('root', '123456'), ('gyk', '123456'), ('zjg123', '123456'))
    )
    def test_post_recommend(self, client, auth_client, username, password):
        auth_client.login(username, password)

        with client:
            rv = client.post('/img', json={
                'img': [1, 2, 34]
            })

            assert rv.status_code == 200
            data = rv.get_json()
            assert data == 'success'
