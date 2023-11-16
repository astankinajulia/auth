import datetime

from flask import Blueprint, current_app, redirect
from flask_restx import Api, reqparse, Resource

from db.tiny_url_service import get_url, increase_counter
from db.user_service import user_service_db

confirm_email_bp = Blueprint('confirm_email_bp', __name__)

api = Api(
    confirm_email_bp,
    doc='/confirm_email/doc',
    title='Confirm Email API',
    description='Confirm email tiny-url with redirection and confirming.',
    default='ConfirmEmail',
    default_label='ConfirmEmail',
)

parser = reqparse.RequestParser()
parser.add_argument('user_id', type=str, help='user_id')
parser.add_argument('timestamp', type=int, help='time when url become invalid')
parser.add_argument('redirect', type=str, help='redirect url')


@api.route('/confirm_email/')
class Confirm(Resource):
    def get(self):
        """Confirm email."""
        current_app.logger.info('Confirm email api')
        args = parser.parse_args()

        current_app.logger.info(f'Confirm email api for user {args["user_id"]}')
        current_app.logger.info(
            f'Url exp date={datetime.datetime.utcfromtimestamp(args["timestamp"])}, '
            f'now={datetime.datetime.utcnow()}')

        if datetime.datetime.utcfromtimestamp(args['timestamp']) < datetime.datetime.utcnow():
            current_app.logger.info(f'Url expired, timestamp={args["timestamp"]}')
            api.abort('404', 'Url expired')

        user_service_db.confirm_email(args['user_id'])

        return redirect(args['redirect'])


@api.route('/tiny/<short_url>')
class RedirectFromShortUrl(Resource):
    def get(self, short_url):
        """Redirect from short url to full url."""
        current_app.logger.info(f'Redirect from short url {short_url} to full url api')

        url = get_url(short_url)

        if url:
            increase_counter(url.short_url)
            return redirect(url.full_url)
        else:
            current_app.logger.info(f'Short url={short_url} not found')
            api.abort(404, 'Short url not found')
