import pytest


class Notice:
    @staticmethod
    def test_get_all_notice(client, auth_client):
        auth_client.login()

        with client:
            client.get('/notice')
