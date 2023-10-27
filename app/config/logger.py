import json
import logging
from datetime import datetime

from flask import request
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

        json_message = {
            '@timestamp': f'{datetime.utcnow().isoformat()}Z',
            'logger': record.name,
            'level': record.levelname,
            'data': {
                'message': message,
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
            'formatter': 'default',
        },
        'werkzeug': {
            'class': 'logging.StreamHandler',
            # 'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'gunicorn': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
    },
    'root': {
        # 'level': 'INFO',
        'handlers': ['wsgi', 'werkzeug', 'gunicorn'],
    },
}
