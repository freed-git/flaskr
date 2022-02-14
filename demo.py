import os
from flask import Flask
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor, ConsoleSpanExporter)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
import sqlite3


provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "demo"}))
# exporter = ConsoleSpanExporter()

exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

app = Flask(__name__)

FlaskInstrumentor().instrument_app(app)
LoggingInstrumentor().instrument(set_logging_format=True)
SQLite3Instrumentor().instrument()

@app.route('/')
def index():

    cnx = sqlite3.connect('example.db')
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO test (testField) VALUES (123)")
    cursor.close()
    cnx.close()

    return 'Web App with Python Flask!'

if __name__ == "__main__":
    app.run(host='0.0.0.0')
