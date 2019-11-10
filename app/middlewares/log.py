from flask import Flask, session, request, Response


def log_mid(app: Flask):
    @app.before_request
    def before_log():
        app.logger.info({
            'url': request.url,
            'method': request.method,
            'body': request.json,
            'user': session.get('user_id')
        })

    @app.after_request
    def after_log(response: Response):
        app.logger.info({
            'status': response.status_code,
            'body': response.json
        })
        return response
