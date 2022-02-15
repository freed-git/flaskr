from flask import Flask
import requests
import os
import logging
# OTEL
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
# import sqlite3

def create_app(test_config=None):
    # OTEL
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: "flaskr"})
        )
    )

    # exporter = ConsoleSpanExporter()
    exporter = JaegerExporter(
        agent_host_name="tempo-distributed-distributor.tempo-distributed",
        agent_port=6831,
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(exporter)
    )

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.ERROR)

    # OTEL
    FlaskInstrumentor().instrument_app(app)
    LoggingInstrumentor().instrument()
    SQLite3Instrumentor().instrument()

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

    @app.route('/health')
    def hello():
        return 'OK'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
