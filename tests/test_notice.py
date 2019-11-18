import pytest


class TestNotice:
    @pytest.mark.parametrize(
        ('username', 'password'),
        (('root', '123456'), ('gyk', '123456'), ('zjg123', '123456'))
    )
    def test_get_all_notice(self, client, auth_client, username, password):
        auth_client.login(username, password)

        with client:
            rv = client.get('/notice')
            assert rv.status_code == 200
            data = rv.get_json()
            assert data['status'] == 'success'

    @pytest.mark.parametrize(
        ('username', 'password'),
        (('root', '123456'), ('gyk', '123456'), ('zjg123', '123456'))
    )
    def test_get_detail_notice(self, client, auth_client, username, password):
        auth_client.login(username, password)

        with client:
            rv = client.get('/notice/2')
            assert rv.status_code == 200
            data = rv.get_json()
            assert data['status'] == 'success'

    @pytest.mark.parametrize(
        ('username', 'password', 'code', 'msg'),
        (('root', '123456', 200, 'success'), ('gyk', '123456', 200, 'success'), ('zjg123', '123456', 401, 'error'))
    )
    def test_post_notice(self, client, auth_client, username, password, code, msg):
        auth_client.login(username, password)

        with client:
            rv = client.post('/notice', json={
                'title': 'test',
                'is_top': '0',
                'type': 2
            })
            assert rv.status_code == code
            data = rv.get_json()
            assert data['status'] == msg

    @pytest.mark.parametrize(
        ('username', 'password', 'code', 'msg', 'notice'),
        (('root', '123456', 200, 'success', [5]),
         ('gyk', '123456', 500, 'error', [6]),
         ('zjg123', '123456', 401, 'error', []))
    )
    def test_delete_notice(self, client, auth_client, username, password, code, msg, notice):
        auth_client.login(username, password)

        with client:
            rv = client.delete('/notice', json={
                'notice_id': notice
            })
            assert rv.status_code == code
            data = rv.get_json()
            assert data['status'] == msg
