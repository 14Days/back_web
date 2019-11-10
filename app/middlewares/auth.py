from flask import Blueprint, session
from app.utils.warp import fail_warp
from app.utils.errors import errors


def auth_mid(page: Blueprint, role: int):
    @page.before_request
    def get_user():
        user_id = session.get('user_id')
        user_type = session.get('type')

        if user_id is None:
            return fail_warp(errors['402']), 401

        if user_type > role:
            return fail_warp(errors['403']), 401
