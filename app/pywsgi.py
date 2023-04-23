from gevent import monkey

monkey.patch_all()

from gevent.pywsgi import WSGIServer  # noqa

from app import app  # noqa

http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()
