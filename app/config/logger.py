import json
import logging
from datetime import datetime

from flask import has_request_context, request
from pythonjsonlogger import jsonlogger


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request.headers.get('X-Request-Id')
        return True


class JsonLoggerFormatter(jsonlogger.JsonFormatter):

    def format(self, record: logging.LogRecord):
        message = record.getMessage()
        if message.find('\\u') > 0:
            message = message.encode('utf_8').decode('unicode_escape')

        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None

        json_message = {
            '@timestamp': f'{datetime.utcnow().isoformat()}Z',
            'logger': record.name,
            'level': record.levelname,
            'url': record.url,
            'remote_addr': record.remote_addr,
            'data': {
                'message': message,
                'x-request-id': getattr(record, 'request_id', None),
                'method': record.method,
            }
        }

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            json_message['exception'] = record.exc_text
        if record.stack_info:
            json_message['stack_trace'] = self.formatStack(record.stack_info)
        return json.dumps(json_message, ensure_ascii=False)


LOGGING_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': True,

    'filters': {
        'request_id': {
            '()': RequestIdFilter,
        },
    },
    'formatters': {
        'default': {'()': JsonLoggerFormatter},
        'text': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'filters': ['request_id'],
            'formatter': 'default',
        },
        'werkzeug': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'gunicorn': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
    },
    'root': {
        'handlers': ['wsgi', 'werkzeug', 'gunicorn'],
    },
}
