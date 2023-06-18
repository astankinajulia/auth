from config.settings import Config
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)


def configure_tracer() -> None:
    resource = Resource(attributes={SERVICE_NAME: Config.SERVICE_NAME})
    provider = TracerProvider(resource=resource)

    trace.set_tracer_provider(provider)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=Config.JAEGER_HOST,
                agent_port=Config.JAEGER_PORT,
            )
        )
    )
    # to see traces in console
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


tracer = trace.get_tracer(__name__)


def trace_func(func):
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__):
            return func(*args, **kwargs)

    return wrapper
