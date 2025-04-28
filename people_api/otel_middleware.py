"""OpenTelemetry logging middleware for FastAPI."""

from collections.abc import Awaitable, Callable

import jwt
from fastapi import Request, Response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource(attributes={"service.name": "mensa-api"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="jaeger:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


async def otel_logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware to log request and response payloads."""
    firebase_token: str = request.headers.get("Authorization", "")
    req_body: bytes = await request.body()
    with tracer.start_as_current_span("http-request") as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        if firebase_token:
            token: str = (
                firebase_token[7:] if firebase_token.startswith("Bearer ") else firebase_token
            )
            try:
                decoded: dict = jwt.decode(token, options={"verify_signature": False})
                email: str = decoded.get("email", "unknown")
                span.set_attribute("firebase.email", email)
            except jwt.InvalidTokenError as e:
                span.set_attribute("firebase.decode_error", str(e))
        try:
            payload: str = req_body.decode("utf-8")
            span.set_attribute("request.payload", payload)
        except UnicodeDecodeError:
            span.set_attribute("request.payload", str(req_body))
        response: Response = await call_next(request)
        resp_body: bytes = b""
        if hasattr(response, "body_iterator"):
            async for chunk in response.body_iterator:
                resp_body += chunk
            response = Response(
                content=resp_body,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        elif hasattr(response, "body"):
            if isinstance(response.body, bytes):
                resp_body = response.body
            else:
                resp_body = str(response.body).encode("utf-8")
        span.set_attribute("response.payload", resp_body.decode("utf-8", errors="replace"))
        return response
