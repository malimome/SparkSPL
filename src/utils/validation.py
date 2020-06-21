"""Input validation shared by the API and the query generator."""
import re
import uuid

import settings


class ValidationError(ValueError):
    pass


class NotFoundError(KeyError):
    def __str__(self):
        return str(self.args[0]) if self.args else "Not found"


_NAME_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-]{0,127}$")
_INDEX_PATTERN_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-*]{0,127}$")
# Absolute ISO-8601 or relative expressions such as "now", "now-1h", "-15m", "now-d".
_TIME_RE = re.compile(
    r"^(now([+-]\d*[a-zA-Z]+)?|[+-]?\d+[a-zA-Z]+|\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?)$"
)
SOURCE_TYPES = ("default", "elastic", "hadoop", "mysql", "mssql", "postgresql", "generative")


def name(value, what="name"):
    if not isinstance(value, str) or not _NAME_RE.match(value):
        raise ValidationError("Invalid %s: use letters, digits, '_', '-' and '.' (max 128)" % what)
    return value


def index_pattern(value):
    if not isinstance(value, str) or not _INDEX_PATTERN_RE.match(value):
        raise ValidationError("Invalid index pattern")
    return value


def uuid_str(value, what="id"):
    try:
        return str(uuid.UUID(str(value)))
    except ValueError:
        raise ValidationError("Invalid %s" % what)


def time_expr(value, what="time"):
    if not isinstance(value, str) or not _TIME_RE.match(value.strip()):
        raise ValidationError("Invalid %s expression" % what)
    return value.strip()


def query(value):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Query must be a non-empty string")
    if len(value) > settings.MAX_QUERY_LENGTH:
        raise ValidationError("Query is too long")
    return value


def source_type(value):
    if value not in SOURCE_TYPES:
        raise ValidationError("Invalid source type")
    return value
