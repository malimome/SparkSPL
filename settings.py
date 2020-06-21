"""Runtime settings, all overridable through SPARKIFY_* environment variables."""
import os


def _bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# Never enable debug in production: it also enables the "testing" job shortcut.
FLASK_DEBUG = _bool("SPARKIFY_DEBUG", False)

# API keys accepted in the X-API-Key header (comma separated). Empty means every
# request is rejected unless SPARKIFY_DISABLE_AUTH is set (local development only).
API_KEYS = [k.strip() for k in os.environ.get("SPARKIFY_API_KEYS", "").split(",") if k.strip()]
DISABLE_AUTH = _bool("SPARKIFY_DISABLE_AUTH", False)

# Origins allowed by CORS (comma separated); empty disables CORS headers.
CORS_ORIGINS = [o.strip() for o in os.environ.get("SPARKIFY_CORS_ORIGINS", "").split(",") if o.strip()]

DATA_DIR = os.environ.get(
    "SPARKIFY_DATA_DIR",
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "static"),
)

LIVY_URL = os.environ.get("SPARKIFY_LIVY_URL", "http://localhost:8998")
LIVY_PROXY_USER = os.environ.get("SPARKIFY_LIVY_PROXY_USER", "")
LIVY_SESSION_TIMEOUT = int(os.environ.get("SPARKIFY_LIVY_SESSION_TIMEOUT", "300"))
HTTP_TIMEOUT = float(os.environ.get("SPARKIFY_HTTP_TIMEOUT", "30"))

ES_HOST = os.environ.get("SPARKIFY_ES_HOST", "localhost")
ES_PORT = os.environ.get("SPARKIFY_ES_PORT", "9200")

JOB_TTL_SECONDS = int(os.environ.get("SPARKIFY_JOB_TTL", "600"))
BLOCKING_TIMEOUT = int(os.environ.get("SPARKIFY_BLOCKING_TIMEOUT", "300"))
MAX_QUERY_LENGTH = 10000
