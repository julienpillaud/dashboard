import logfire

from app.api.app import create_fastapi_app
from app.api.dependencies.app import get_settings

settings = get_settings()
logfire.configure(
    send_to_logfire="if-token-present",
    token=settings.logfire_token,
    service_name="app",
    environment=settings.environment,
    console=False,
)
logfire.instrument_pymongo(capture_statement=True)
app = create_fastapi_app(settings=settings)
logfire.instrument_fastapi(app, capture_headers=True, extra_spans=True)
