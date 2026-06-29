# frontend/sql_guard.py
import re

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "GRANT", "REVOKE", "CREATE", "EXEC", "EXECUTE",
]

DEFAULT_ROW_LIMIT = 100


class UnsafeQueryError(Exception):
    """Raised when a generated query fails validation."""
    pass


def validate_query(sql: str) -> str:
    """
    Validates that a SQL string is a single, read-only SELECT statement.
    Returns the (possibly limit-modified) query if it passes, or raises
    UnsafeQueryError if it doesn't.

    This is a defense-in-depth layer, not the only protection - the
    analytics_readonly DB role itself can't write or alter regardless
    of what SQL reaches it. This catches bad queries before they even
    hit the database, and keeps the app from returning confusing
    permission-denied errors instead of a clear explanation.
    """
    cleaned = sql.strip().rstrip(";")

    # Reject statement chaining (a second statement smuggled in via ;)
    if ";" in cleaned:
        raise UnsafeQueryError("Multiple statements are not allowed.")

    # Must start with SELECT (case-insensitive)
    if not re.match(r"^\s*SELECT\s", cleaned, re.IGNORECASE):
        raise UnsafeQueryError("Only SELECT statements are allowed.")

    # Reject any forbidden keyword appearing anywhere in the query,
    # as a whole word (so e.g. a column named 'updated_at' doesn't
    # trigger a false positive on 'UPDATE')
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", cleaned, re.IGNORECASE):
            raise UnsafeQueryError(f"Query contains a forbidden keyword: {keyword}")

    # Enforce a row limit if the query doesn't already have one
    if not re.search(r"\bLIMIT\s+\d+\b", cleaned, re.IGNORECASE):
        cleaned += f" LIMIT {DEFAULT_ROW_LIMIT}"

    return cleaned