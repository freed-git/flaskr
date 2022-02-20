from codecs import BOM_BE
from flask import Flask, make_response
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
from prometheus_client import generate_latest
# from prometheus_client.openmetrics.exposition import generate_latest
from prometheus_client import CollectorRegistry, REGISTRY, CONTENT_TYPE_LATEST



from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client.exposition import make_wsgi_app

# registry = CollectorRegistry()

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

    # logging_format = '{"asctime": "%(asctime)s","levelname": "%(levelname)s","name": "[%(name)s]","filename": "%(filename)s","lineno": "%(lineno)d","trace_id": "%(otelTraceID)s","span_id": "%(otelSpanID)s","resource_service_name": "%(otelServiceName)s","message": "%(message)s"}'

    LoggingInstrumentor().instrument()

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.ERROR)

    # OTEL
    FlaskInstrumentor().instrument_app(app)
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

    # @app.route('/metrics')
    # def metrics():
    #     # return generate_latest(registry=REGISTRY)
    #     data = generate_latest(REGISTRY)

    #     response = make_response(data)
    #     response.headers['Content-Type'] = CONTENT_TYPE_LATEST
    #     response.headers['Content-Length'] = str(len(data))

    #     return response

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app(registry=REGISTRY)
    })

    return app
