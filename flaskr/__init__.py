import os
from opentelemetry.instrumentation.flask import FlaskInstrumentor
# from logging.config import dictConfig
from flask import Flask

# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/flask/flask.html
# https://grafana.com/docs/tempo/latest/getting-started/
# https://github.com/grafana/agent/blob/v0.8.0/production/kubernetes/agent-tempo.yaml
# https://github.com/grafana/agent

# import logging
# logger = logging.getLogger('waitress')
# logger.setLevel(logging.DEBUG)

import logging


# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://sys.stdout',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'INFO',
#         'handlers': ['wsgi']
#     }
# })

def create_app(test_config=None):
    logging.basicConfig(level=logging.DEBUG)

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    FlaskInstrumentor().instrument_app(app)


    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
