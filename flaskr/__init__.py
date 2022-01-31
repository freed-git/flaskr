from flask import Flask
import requests
import os
import logging
# from opentelemetry import trace
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
# from opentelemetry.sdk.resources import SERVICE_NAME, Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.instrumentation.flask import FlaskInstrumentor
# from opentelemetry.instrumentation.requests import RequestsInstrumentor

# from opentelemetry.sdk.trace.export import (
#     BatchSpanProcessor,
#     ConsoleSpanExporter
# )


def create_app(test_config=None):
    logging.basicConfig(level=logging.DEBUG)

    # trace.set_tracer_provider(
    #     TracerProvider(
    #         resource=Resource.create({SERVICE_NAME: "flaskr"})
    #     )
    # )

    # jaeger_exporter = JaegerExporter(
    #     agent_host_name="tempo-distributed-distributor.tempo-distributed",
    #     agent_port=6831,
    # )

    # trace.get_tracer_provider().add_span_processor(
    #     BatchSpanProcessor(jaeger_exporter)
    # )

    # trace.set_tracer_provider(TracerProvider())
    # trace.get_tracer_provider().add_span_processor(
    #     BatchSpanProcessor(ConsoleSpanExporter())
    # )

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # FlaskInstrumentor().instrument_app(app)
    # RequestsInstrumentor().instrument()

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
        # tracer = trace.get_tracer(__name__)
        # with tracer.start_as_current_span("example-request"):
        requests.get("http://google.com")

        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
