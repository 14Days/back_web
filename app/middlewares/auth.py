from flask import Blueprint, session, request
from app.utils.warp import fail_warp
from app.utils.errors import errors


def auth_mid(page: Blueprint):
    @page.before_request
    def get_user():
        user_id = session.get('user_id')

        if user_id is None and request.method != 'OPTIONS':
            return fail_warp(errors['402'])

        # if user_type > role:
        #     return fail_warp(errors['403']), 401
