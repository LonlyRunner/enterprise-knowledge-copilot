"""Optional OpenTelemetry bootstrap.

The application remains runnable without OTel packages. Installing the
observability extra and setting OTEL_EXPORTER_OTLP_ENDPOINT enables automatic
FastAPI/HTTP spans without changing the RAG code.
"""
import logging
import os

logger = logging.getLogger(__name__)


def setup_opentelemetry(app) -> bool:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return False
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry import trace
    except ImportError:
        logger.warning("OTEL endpoint is configured but observability extras are not installed")
        return False
    provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "enterprise-knowledge-copilot")}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    return True
