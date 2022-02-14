import sqlite3
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor


trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "sqlite_test"})
    )
)

# exporter = ConsoleSpanExporter()
exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(exporter)
)


SQLite3Instrumentor().instrument()



cnx = sqlite3.connect('example.db')
cursor = cnx.cursor()
cursor.execute("INSERT INTO test (testField) VALUES (123)")
cursor.close()
cnx.close()




# CREATE TABLE test (
# 	testField INTEGER PRIMARY KEY
# );